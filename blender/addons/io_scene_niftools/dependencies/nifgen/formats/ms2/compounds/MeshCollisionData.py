from nifgen.array import Array
from nifgen.base_struct import BaseStruct
from nifgen.formats.ms2.imports import name_type_map


class MeshCollisionData(BaseStruct):

	__name__ = 'MeshCollisionData'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# usually zero, nonzero in JWE2 dev footplant, [1] used as salt for tri indices
		self.tris_salt = Array(self.context, 0, None, (0,), name_type_map['Uint'])
		self.vertices_addr = name_type_map['Empty'](self.context, 0, None)

		# array of vertices
		self.vertices = Array(self.context, 0, None, (0,), name_type_map['Float'])
		self.triangles_addr = name_type_map['Empty'](self.context, 0, None)

		# triangle indices into vertex list
		self.triangles = Array(self.context, 0, None, (0,), name_type_map['Ushort'])

		# ?
		self.const = name_type_map['Uint'](self.context, 0, None)

		# in JWE redwood: always 37
		self.triangle_flags = Array(self.context, 0, None, (0,), name_type_map['Uint'])

		# might be padding!
		self.zero_end = name_type_map['Uint'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'tris_salt', Array, (0, None, (4,), name_type_map['Uint']), (False, None), (None, True)
		yield 'vertices_addr', name_type_map['Empty'], (0, None), (False, None), (None, None)
		yield 'vertices', Array, (0, None, (None, 3,), name_type_map['Float']), (False, None), (None, None)
		yield 'triangles_addr', name_type_map['Empty'], (0, None), (False, None), (None, None)
		yield 'triangles', Array, (0, None, (None, 3,), name_type_map['Ushort']), (False, None), (None, None)
		yield 'const', name_type_map['Uint'], (0, None), (False, None), (lambda context: context.version <= 47, None)
		yield 'triangle_flags', Array, (0, None, (None,), name_type_map['Uint']), (False, None), (lambda context: context.version <= 47, True)
		yield 'zero_end', name_type_map['Uint'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		if instance.arg.has_sub_coll_chunk:
			yield 'tris_salt', Array, (0, None, (4,), name_type_map['Uint']), (False, None)
		yield 'vertices_addr', name_type_map['Empty'], (0, None), (False, None)
		yield 'vertices', Array, (0, None, (instance.arg.vertex_count, 3,), name_type_map['Float']), (False, None)
		yield 'triangles_addr', name_type_map['Empty'], (0, None), (False, None)
		yield 'triangles', Array, (0, None, (instance.arg.tri_count, 3,), name_type_map['Ushort']), (False, None)
		if instance.context.version <= 47:
			yield 'const', name_type_map['Uint'], (0, None), (False, None)
		if instance.context.version <= 47 and instance.const:
			yield 'triangle_flags', Array, (0, None, (instance.arg.sub_coll_chunk.tri_flags_count,), name_type_map['Uint']), (False, None)
		yield 'zero_end', name_type_map['Uint'], (0, None), (False, None)

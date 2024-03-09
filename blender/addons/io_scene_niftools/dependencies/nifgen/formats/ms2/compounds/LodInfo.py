from nifgen.base_struct import BaseStruct
from nifgen.formats.ms2.imports import name_type_map


class LodInfo(BaseStruct):

	"""
	DLA, ZTUAC - 16 bytes
	JWE, PZ, JWE2 - 20 bytes
	JWE2 Biosyn - 12 bytes, skips the vert / tris counts
	"""

	__name__ = 'LodInfo'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# FFFF
		self.full = name_type_map['Short'](self.context, 0, None)

		# 7F7F
		self.half = name_type_map['Short'](self.context, 0, None)

		# increasing
		self.lod_index = name_type_map['Ushort'](self.context, 0, None)

		# usually first lod is 900
		self.distance = name_type_map['Float'](self.context, 0, None)

		# matches the buffer index used by this LOD's meshes
		self.stream_index = name_type_map['Ushort'](self.context, 0, None)

		# Last bone that is used by this lod's models; usually decreases with increasing lod index to decimate bones. However: JWE detailobjects - nat_groundcover_searocket_patchy_02 due to dedicated lod nodes
		self.bone_index = name_type_map['Ushort'](self.context, 0, None)

		# first object for this lod in objects list
		self.first_object_index = name_type_map['Ushort'](self.context, 0, None)
		self.first_object_index_1 = name_type_map['Ushort'](self.context, 0, None)
		self.first_object_index_2 = name_type_map['Ushort'](self.context, 0, None)

		# not included in interval (python style indexing)
		self.last_object_index = name_type_map['Ushort'](self.context, 0, None)

		# vertex count of lod, sum of all vertex counts that are attached to this lod; rendered count, including duped models
		self.vertex_count = name_type_map['Uint'](self.context, 0, None)

		# number of index entries in the triangle index list; (not: number of triangles, byte count of tri buffer); rendered count, including duped models
		self.tri_index_count = name_type_map['Uint'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'full', name_type_map['Short'], (0, None), (False, None), (lambda context: context.version <= 13, None)
		yield 'half', name_type_map['Short'], (0, None), (False, None), (lambda context: context.version <= 13, None)
		yield 'lod_index', name_type_map['Ushort'], (0, None), (False, None), (lambda context: context.version <= 13, None)
		yield 'distance', name_type_map['Float'], (0, None), (False, None), (lambda context: context.version >= 32, None)
		yield 'stream_index', name_type_map['Ushort'], (0, None), (False, None), (lambda context: context.version >= 32, None)
		yield 'bone_index', name_type_map['Ushort'], (0, None), (False, None), (None, None)
		yield 'first_object_index', name_type_map['Ushort'], (0, None), (False, None), (None, None)
		yield 'first_object_index_1', name_type_map['Ushort'], (0, None), (False, None), (lambda context: context.version <= 13, None)
		yield 'first_object_index_2', name_type_map['Ushort'], (0, None), (False, None), (lambda context: context.version <= 13, None)
		yield 'last_object_index', name_type_map['Ushort'], (0, None), (False, None), (None, None)
		yield 'vertex_count', name_type_map['Uint'], (0, None), (False, None), (lambda context: 32 <= context.version <= 51, None)
		yield 'tri_index_count', name_type_map['Uint'], (0, None), (False, None), (lambda context: 32 <= context.version <= 51, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		if instance.context.version <= 13:
			yield 'full', name_type_map['Short'], (0, None), (False, None)
			yield 'half', name_type_map['Short'], (0, None), (False, None)
			yield 'lod_index', name_type_map['Ushort'], (0, None), (False, None)
		if instance.context.version >= 32:
			yield 'distance', name_type_map['Float'], (0, None), (False, None)
			yield 'stream_index', name_type_map['Ushort'], (0, None), (False, None)
		yield 'bone_index', name_type_map['Ushort'], (0, None), (False, None)
		yield 'first_object_index', name_type_map['Ushort'], (0, None), (False, None)
		if instance.context.version <= 13:
			yield 'first_object_index_1', name_type_map['Ushort'], (0, None), (False, None)
			yield 'first_object_index_2', name_type_map['Ushort'], (0, None), (False, None)
		yield 'last_object_index', name_type_map['Ushort'], (0, None), (False, None)
		if 32 <= instance.context.version <= 51:
			yield 'vertex_count', name_type_map['Uint'], (0, None), (False, None)
			yield 'tri_index_count', name_type_map['Uint'], (0, None), (False, None)

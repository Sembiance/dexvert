from nifgen.array import Array
from nifgen.formats.ms2.imports import name_type_map
from nifgen.formats.ovl_base.compounds.MemStruct import MemStruct


class ModelInfo(MemStruct):

	"""
	Describes one model, corresponding to a virtual .mdl2 file
	JWE2 - 192 bytes
	JWE2 Biosyn - 160 bytes
	"""

	__name__ = 'ModelInfo'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# ??
		self.unk_dla = name_type_map['Uint64'](self.context, 0, None)

		# the smallest coordinates across all axes
		self.bounds_min = name_type_map['Vector3'](self.context, 0, None)

		# related to the inverse of pack_base
		self.precision = name_type_map['Float'](self.context, 0, None)

		# the biggest coordinates across all axes
		self.bounds_max = name_type_map['Vector3'](self.context, 0, None)

		# scale: pack_base / 512, also added as offset
		self.pack_base = name_type_map['Float'](self.context, 0, None)

		# cog? medium of bounds?
		self.center = name_type_map['Vector3'](self.context, 0, None)

		# probably from center to max
		self.radius = name_type_map['Float'](self.context, 0, None)

		# seen 6 or 1, matches lod count
		self.num_lods_2 = name_type_map['Uint64'](self.context, 0, None)

		# zero
		self.zero = name_type_map['Uint64'](self.context, 0, None)

		# verbatim repeat
		self.bounds_min_repeat = name_type_map['Vector3'](self.context, 0, None)

		# verbatim repeat
		self.bounds_max_repeat = name_type_map['Vector3'](self.context, 0, None)
		self.num_materials = name_type_map['Ushort'](self.context, 0, None)
		self.num_lods = name_type_map['Ushort'](self.context, 0, None)
		self.num_objects = name_type_map['Ushort'](self.context, 0, None)

		# count of MeshData fragments for the mdl2 this struct refers to
		self.num_meshes = name_type_map['Ushort'](self.context, 0, None)

		# ?
		self.last_count = name_type_map['Ushort'](self.context, 0, None)

		# this has influence on whether newly added shells draw correctly; for PZ usually 4, except for furry animals; ZT african ele female
		self.render_flag = name_type_map['RenderFlag'](self.context, 0, None)

		# ?
		self.unks = Array(self.context, 0, None, (0,), name_type_map['Ushort'])
		self.pad = Array(self.context, 0, None, (0,), name_type_map['Ushort'])
		self.zeros = Array(self.context, 0, None, (0,), name_type_map['Uint64'])

		# used to increment skeleton index
		self.increment_flag = name_type_map['Uint64'](self.context, 0, None)
		self.zero_0 = name_type_map['Uint64'](self.context, 0, None)
		self.zero_1 = name_type_map['Uint64'](self.context, 0, None)
		self.zero_2 = name_type_map['Uint64'](self.context, 0, None)
		self.materials = name_type_map['ArrayPointer'](self.context, self.num_materials, name_type_map['MaterialName'])
		self.lods = name_type_map['ArrayPointer'](self.context, self.num_lods, name_type_map['LodInfo'])
		self.objects = name_type_map['ArrayPointer'](self.context, self.num_objects, name_type_map['Object'])
		self.meshes = name_type_map['ArrayPointer'](self.context, self.num_meshes, name_type_map['MeshDataWrap'])

		# points to the start of this ModelInfo's model, usually starts at materials
		# stays the same for successive mdl2s in the same model; or points to nil if no models are present
		self.first_model = name_type_map['Pointer'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'unk_dla', name_type_map['Uint64'], (0, None), (False, None), (lambda context: context.version <= 7, None)
		yield 'bounds_min', name_type_map['Vector3'], (0, None), (False, None), (None, None)
		yield 'precision', name_type_map['Float'], (0, None), (False, None), (lambda context: 47 <= context.version <= 51, None)
		yield 'bounds_max', name_type_map['Vector3'], (0, None), (False, None), (None, None)
		yield 'pack_base', name_type_map['Float'], (0, None), (False, None), (lambda context: 47 <= context.version <= 51, None)
		yield 'center', name_type_map['Vector3'], (0, None), (False, None), (None, None)
		yield 'radius', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'num_lods_2', name_type_map['Uint64'], (0, None), (False, None), (lambda context: 48 <= context.version <= 51, None)
		yield 'zero', name_type_map['Uint64'], (0, None), (False, None), (lambda context: 48 <= context.version <= 51, None)
		yield 'bounds_min_repeat', name_type_map['Vector3'], (0, None), (False, None), (lambda context: context.version >= 32, None)
		yield 'bounds_max_repeat', name_type_map['Vector3'], (0, None), (False, None), (lambda context: context.version >= 32, None)
		yield 'num_materials', name_type_map['Ushort'], (0, None), (False, None), (None, None)
		yield 'num_lods', name_type_map['Ushort'], (0, None), (False, None), (None, None)
		yield 'num_objects', name_type_map['Ushort'], (0, None), (False, None), (None, None)
		yield 'num_meshes', name_type_map['Ushort'], (0, None), (False, None), (None, None)
		yield 'last_count', name_type_map['Ushort'], (0, None), (False, None), (None, None)
		yield 'render_flag', name_type_map['RenderFlag'], (0, None), (False, None), (None, None)
		yield 'unks', Array, (0, None, (7,), name_type_map['Ushort']), (False, None), (None, None)
		yield 'pad', Array, (0, None, (3,), name_type_map['Ushort']), (False, None), (None, None)
		yield 'materials', name_type_map['ArrayPointer'], (None, name_type_map['MaterialName']), (False, None), (None, None)
		yield 'lods', name_type_map['ArrayPointer'], (None, name_type_map['LodInfo']), (False, None), (None, None)
		yield 'objects', name_type_map['ArrayPointer'], (None, name_type_map['Object']), (False, None), (None, None)
		yield 'meshes', name_type_map['ArrayPointer'], (None, name_type_map['MeshDataWrap']), (False, None), (None, None)
		yield 'first_model', name_type_map['Pointer'], (0, None), (False, None), (None, None)
		yield 'zeros', Array, (0, None, (4,), name_type_map['Uint64']), (False, None), (lambda context: context.version == 13, None)
		yield 'zeros', Array, (0, None, (2,), name_type_map['Uint64']), (False, None), (lambda context: context.version == 7, None)
		yield 'increment_flag', name_type_map['Uint64'], (0, None), (False, None), (None, None)
		yield 'zero_0', name_type_map['Uint64'], (0, None), (False, None), (lambda context: not (context.version == 7), None)
		yield 'zero_1', name_type_map['Uint64'], (0, None), (False, None), (lambda context: not (context.version == 32), None)
		yield 'zero_2', name_type_map['Uint64'], (0, None), (False, None), (lambda context: 47 <= context.version <= 51, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		if instance.context.version <= 7:
			yield 'unk_dla', name_type_map['Uint64'], (0, None), (False, None)
		yield 'bounds_min', name_type_map['Vector3'], (0, None), (False, None)
		if 47 <= instance.context.version <= 51:
			yield 'precision', name_type_map['Float'], (0, None), (False, None)
		yield 'bounds_max', name_type_map['Vector3'], (0, None), (False, None)
		if 47 <= instance.context.version <= 51:
			yield 'pack_base', name_type_map['Float'], (0, None), (False, None)
		yield 'center', name_type_map['Vector3'], (0, None), (False, None)
		yield 'radius', name_type_map['Float'], (0, None), (False, None)
		if 48 <= instance.context.version <= 51:
			yield 'num_lods_2', name_type_map['Uint64'], (0, None), (False, None)
			yield 'zero', name_type_map['Uint64'], (0, None), (False, None)
		if instance.context.version >= 32:
			yield 'bounds_min_repeat', name_type_map['Vector3'], (0, None), (False, None)
			yield 'bounds_max_repeat', name_type_map['Vector3'], (0, None), (False, None)
		yield 'num_materials', name_type_map['Ushort'], (0, None), (False, None)
		yield 'num_lods', name_type_map['Ushort'], (0, None), (False, None)
		yield 'num_objects', name_type_map['Ushort'], (0, None), (False, None)
		yield 'num_meshes', name_type_map['Ushort'], (0, None), (False, None)
		yield 'last_count', name_type_map['Ushort'], (0, None), (False, None)
		yield 'render_flag', name_type_map['RenderFlag'], (0, None), (False, None)
		yield 'unks', Array, (0, None, (7,), name_type_map['Ushort']), (False, None)
		yield 'pad', Array, (0, None, (3,), name_type_map['Ushort']), (False, None)
		yield 'materials', name_type_map['ArrayPointer'], (instance.num_materials, name_type_map['MaterialName']), (False, None)
		yield 'lods', name_type_map['ArrayPointer'], (instance.num_lods, name_type_map['LodInfo']), (False, None)
		yield 'objects', name_type_map['ArrayPointer'], (instance.num_objects, name_type_map['Object']), (False, None)
		yield 'meshes', name_type_map['ArrayPointer'], (instance.num_meshes, name_type_map['MeshDataWrap']), (False, None)
		yield 'first_model', name_type_map['Pointer'], (0, None), (False, None)
		if instance.context.version == 13:
			yield 'zeros', Array, (0, None, (4,), name_type_map['Uint64']), (False, None)
		if instance.context.version == 7:
			yield 'zeros', Array, (0, None, (2,), name_type_map['Uint64']), (False, None)
		yield 'increment_flag', name_type_map['Uint64'], (0, None), (False, None)
		if not (instance.context.version == 7):
			yield 'zero_0', name_type_map['Uint64'], (0, None), (False, None)
		if not (instance.context.version == 32):
			yield 'zero_1', name_type_map['Uint64'], (0, None), (False, None)
		if 47 <= instance.context.version <= 51:
			yield 'zero_2', name_type_map['Uint64'], (0, None), (False, None)

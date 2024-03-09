from nifgen.array import Array
from nifgen.base_struct import BaseStruct
from nifgen.formats.ms2.imports import name_type_map


class Model(BaseStruct):

	__name__ = 'Model'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.start_ref = name_type_map['Empty'](self.context, 0, None)

		# name pointers for each material
		self.materials = Array(self.context, 0, None, (0,), name_type_map['MaterialName'])

		# lod info for each level, only present if models are present (despite the count sometimes saying otherwise!)
		self.lods = Array(self.context, 0, None, (0,), name_type_map['LodInfo'])

		# instantiate the meshes with materials
		self.objects = Array(self.context, 0, None, (0,), name_type_map['Object'])
		self.mesh_aligner = name_type_map['PadAlign'](self.context, 8, self.start_ref)

		# mesh data blocks for this model
		self.meshes = Array(self.context, 0, None, (0,), name_type_map['MeshDataWrap'])

		# ?
		self.pre_bones = name_type_map['DLAPreBones'](self.context, 0, None)

		# see if it is a flag for ztuac too, so might be totally wrong here
		self.floatsy = Array(self.context, 0, None, (0,), name_type_map['FloatsY'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'start_ref', name_type_map['Empty'], (0, None), (False, None), (None, None)
		yield 'materials', Array, (0, None, (None,), name_type_map['MaterialName']), (False, None), (None, None)
		yield 'lods', Array, (0, None, (None,), name_type_map['LodInfo']), (False, None), (None, None)
		yield 'objects', Array, (0, None, (None,), name_type_map['Object']), (False, None), (None, None)
		yield 'mesh_aligner', name_type_map['PadAlign'], (8, None), (False, None), (lambda context: context.version <= 32, None)
		yield 'meshes', Array, (0, None, (None,), name_type_map['MeshDataWrap']), (False, None), (None, None)
		yield 'pre_bones', name_type_map['ZTPreBones'], (0, None), (False, None), (lambda context: context.version == 13, True)
		yield 'pre_bones', name_type_map['DLAPreBones'], (0, None), (False, None), (lambda context: context.version == 7, True)
		yield 'floatsy', Array, (0, None, (None,), name_type_map['FloatsY']), (False, None), (lambda context: context.version <= 32, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'start_ref', name_type_map['Empty'], (0, None), (False, None)
		yield 'materials', Array, (0, None, (instance.arg.num_materials,), name_type_map['MaterialName']), (False, None)
		yield 'lods', Array, (0, None, (instance.arg.num_lods,), name_type_map['LodInfo']), (False, None)
		yield 'objects', Array, (0, None, (instance.arg.num_objects,), name_type_map['Object']), (False, None)
		if instance.context.version <= 32:
			yield 'mesh_aligner', name_type_map['PadAlign'], (8, instance.start_ref), (False, None)
		yield 'meshes', Array, (0, None, (instance.arg.num_meshes,), name_type_map['MeshDataWrap']), (False, None)
		if instance.context.version == 13 and instance.arg.last_count:
			yield 'pre_bones', name_type_map['ZTPreBones'], (0, None), (False, None)
		if instance.context.version == 7 and instance.arg.last_count:
			yield 'pre_bones', name_type_map['DLAPreBones'], (0, None), (False, None)
		if instance.context.version <= 32:
			yield 'floatsy', Array, (0, None, (instance.arg.render_flag,), name_type_map['FloatsY']), (False, None)

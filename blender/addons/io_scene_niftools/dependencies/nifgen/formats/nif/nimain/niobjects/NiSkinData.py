from nifgen.array import Array
from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nimain.niobjects.NiObject import NiObject


class NiSkinData(NiObject):

	"""
	Skinning data.
	"""

	__name__ = 'NiSkinData'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# Offset of the skin from this bone in bind position.
		self.skin_transform = name_type_map['NiTransform'](self.context, 0, None)

		# Number of bones.
		self.num_bones = name_type_map['Uint'](self.context, 0, None)

		# This optionally links a NiSkinPartition for hardware-acceleration information.
		self.skin_partition = name_type_map['Ref'](self.context, 0, name_type_map['NiSkinPartition'])

		# Enables Vertex Weights for this NiSkinData.
		# 1 (default): vertex weights are stored in floats.
		# 15 (compression): vertex weights are stored in half floats (found in 20.3.1.1 Fantasy Frontier Online).
		self.has_vertex_weights = name_type_map['Bool'].from_value(True)

		# Contains offset data for each node that this skin is influenced by.
		self.bone_list = Array(self.context, self.has_vertex_weights, None, (0,), name_type_map['BoneData'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'skin_transform', name_type_map['NiTransform'], (0, None), (False, None), (None, None)
		yield 'num_bones', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'skin_partition', name_type_map['Ref'], (0, name_type_map['NiSkinPartition']), (False, None), (lambda context: 67108866 <= context.version <= 167837696, None)
		yield 'has_vertex_weights', name_type_map['Bool'], (0, None), (False, True), (lambda context: context.version >= 67240192, None)
		yield 'bone_list', Array, (None, None, (None,), name_type_map['BoneData']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'skin_transform', name_type_map['NiTransform'], (0, None), (False, None)
		yield 'num_bones', name_type_map['Uint'], (0, None), (False, None)
		if 67108866 <= instance.context.version <= 167837696:
			yield 'skin_partition', name_type_map['Ref'], (0, name_type_map['NiSkinPartition']), (False, None)
		if instance.context.version >= 67240192:
			yield 'has_vertex_weights', name_type_map['Bool'], (0, None), (False, True)
		yield 'bone_list', Array, (instance.has_vertex_weights, None, (instance.num_bones,), name_type_map['BoneData']), (False, None)
	def get_transform(self):
		"""Return scale, rotation, and translation into a single 4x4 matrix."""
		return self.skin_transform.get_transform()

	def set_transform(self, mat):
		"""Set rotation, transform, and velocity."""
		self.skin_transform.set_transform(mat)

	def apply_scale(self, scale):
		"""Apply scale factor on data.

		>>> from pyffi.formats.nif import NifFormat
		>>> id44 = NifFormat.Matrix44()
		>>> id44.set_identity()
		>>> skelroot = NifFormat.NiNode()
		>>> skelroot.name = 'Scene Root'
		>>> skelroot.set_transform(id44)
		>>> bone1 = NifFormat.NiNode()
		>>> bone1.name = 'bone1'
		>>> bone1.set_transform(id44)
		>>> bone1.translation.x = 10
		>>> skelroot.add_child(bone1)
		>>> geom = NifFormat.NiTriShape()
		>>> geom.set_transform(id44)
		>>> skelroot.add_child(geom)
		>>> skininst = NifFormat.NiSkinInstance()
		>>> geom.skin_instance = skininst
		>>> skininst.skeleton_root = skelroot
		>>> skindata = NifFormat.NiSkinData()
		>>> skininst.data = skindata
		>>> skindata.set_transform(id44)
		>>> geom.add_bone(bone1, {})
		>>> geom.update_bind_position()
		>>> bone1.translation.x
		10.0
		>>> skindata.bone_list[0].skin_transform.translation.x
		-10.0
		>>> import pyffi.spells.nif.fix
		>>> import pyffi.spells.nif
		>>> data = NifFormat.Data()
		>>> data.roots = [skelroot]
		>>> toaster = pyffi.spells.nif.NifToaster()
		>>> toaster.scale = 0.1
		>>> pyffi.spells.nif.fix.SpellScale(data=data, toaster=toaster).recurse()
		pyffi.toaster:INFO:--- fix_scale ---
		pyffi.toaster:INFO:  scaling by factor 0.100000
		pyffi.toaster:INFO:  ~~~ NiNode [Scene Root] ~~~
		pyffi.toaster:INFO:	~~~ NiNode [bone1] ~~~
		pyffi.toaster:INFO:	~~~ NiTriShape [] ~~~
		pyffi.toaster:INFO:	  ~~~ NiSkinInstance [] ~~~
		pyffi.toaster:INFO:		~~~ NiSkinData [] ~~~
		>>> bone1.translation.x
		1.0
		>>> skindata.bone_list[0].skin_transform.translation.x
		-1.0
		"""

		self.skin_transform.translation.x *= scale
		self.skin_transform.translation.y *= scale
		self.skin_transform.translation.z *= scale

		for skindata in self.bone_list:
			skindata.skin_transform.translation.x *= scale
			skindata.skin_transform.translation.y *= scale
			skindata.skin_transform.translation.z *= scale
			skindata.bounding_sphere.apply_scale(scale)


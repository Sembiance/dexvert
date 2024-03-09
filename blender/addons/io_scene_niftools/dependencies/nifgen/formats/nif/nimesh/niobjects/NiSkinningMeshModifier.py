from nifgen.array import Array
from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nimesh.niobjects.NiMeshModifier import NiMeshModifier


class NiSkinningMeshModifier(NiMeshModifier):

	__name__ = 'NiSkinningMeshModifier'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# USE_SOFTWARE_SKINNING = 0x0001
		# RECOMPUTE_BOUNDS = 0x0002
		self.flags = name_type_map['Ushort'](self.context, 0, None)

		# The root bone of the skeleton.
		self.skeleton_root = name_type_map['Ptr'](self.context, 0, name_type_map['NiAVObject'])

		# The transform that takes the root bone parent coordinate system into the skin coordinate system.
		self.skeleton_transform = name_type_map['NiTransform'](self.context, 0, None)

		# The number of bones referenced by this mesh modifier.
		self.num_bones = name_type_map['Uint'](self.context, 0, None)

		# Pointers to the bone nodes that affect this skin.
		self.bones = Array(self.context, 0, name_type_map['NiAVObject'], (0,), name_type_map['Ptr'])

		# The transforms that go from bind-pose space to bone space.
		self.bone_transforms = Array(self.context, 0, None, (0,), name_type_map['NiTransform'])

		# The bounds of the bones.  Only stored if the RECOMPUTE_BOUNDS bit is set.
		self.bone_bounds = Array(self.context, 0, None, (0,), name_type_map['NiBound'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'flags', name_type_map['Ushort'], (0, None), (False, None), (None, None)
		yield 'skeleton_root', name_type_map['Ptr'], (0, name_type_map['NiAVObject']), (False, None), (None, None)
		yield 'skeleton_transform', name_type_map['NiTransform'], (0, None), (False, None), (None, None)
		yield 'num_bones', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'bones', Array, (0, name_type_map['NiAVObject'], (None,), name_type_map['Ptr']), (False, None), (None, None)
		yield 'bone_transforms', Array, (0, None, (None,), name_type_map['NiTransform']), (False, None), (None, None)
		yield 'bone_bounds', Array, (0, None, (None,), name_type_map['NiBound']), (False, None), (None, True)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'flags', name_type_map['Ushort'], (0, None), (False, None)
		yield 'skeleton_root', name_type_map['Ptr'], (0, name_type_map['NiAVObject']), (False, None)
		yield 'skeleton_transform', name_type_map['NiTransform'], (0, None), (False, None)
		yield 'num_bones', name_type_map['Uint'], (0, None), (False, None)
		yield 'bones', Array, (0, name_type_map['NiAVObject'], (instance.num_bones,), name_type_map['Ptr']), (False, None)
		yield 'bone_transforms', Array, (0, None, (instance.num_bones,), name_type_map['NiTransform']), (False, None)
		if (instance.flags & 2) != 0:
			yield 'bone_bounds', Array, (0, None, (instance.num_bones,), name_type_map['NiBound']), (False, None)

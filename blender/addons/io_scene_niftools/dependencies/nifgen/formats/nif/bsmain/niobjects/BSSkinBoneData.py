import nifgen.formats.nif as NifFormat
from nifgen.array import Array
from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nimain.niobjects.NiObject import NiObject


class BSSkinBoneData(NiObject):

	"""
	Fallout 4 Bone Data
	"""

	__name__ = 'BSSkin::BoneData'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.num_bones = name_type_map['Uint'](self.context, 0, None)
		self.bone_list = Array(self.context, 0, None, (0,), name_type_map['BSSkinBoneTrans'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'num_bones', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'bone_list', Array, (0, None, (None,), name_type_map['BSSkinBoneTrans']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'num_bones', name_type_map['Uint'], (0, None), (False, None)
		yield 'bone_list', Array, (0, None, (instance.num_bones,), name_type_map['BSSkinBoneTrans']), (False, None)

	def apply_scale(self, scale):
		if abs(scale - 1.0) <= NifFormat.EPSILON: return
		super().apply_scale(scale)
		for bone in self.bone_list:
			bone.bounding_sphere.apply_scale(scale)
			bone.translation.x *= scale
			bone.translation.y *= scale
			bone.translation.z *= scale


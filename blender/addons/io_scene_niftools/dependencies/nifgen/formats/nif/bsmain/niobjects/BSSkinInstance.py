from nifgen.array import Array
from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nimain.niobjects.NiObject import NiObject


class BSSkinInstance(NiObject):

	"""
	Fallout 4 Skin Instance
	"""

	__name__ = 'BSSkin::Instance'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.skeleton_root = name_type_map['Ptr'](self.context, 0, name_type_map['NiAVObject'])
		self.data = name_type_map['Ref'](self.context, 0, name_type_map['BSSkinBoneData'])
		self.num_bones = name_type_map['Uint'](self.context, 0, None)
		self.bones = Array(self.context, 0, name_type_map['NiNode'], (0,), name_type_map['Ptr'])
		self.num_scales = name_type_map['Uint'](self.context, 0, None)
		self.scales = Array(self.context, 0, None, (0,), name_type_map['Vector3'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'skeleton_root', name_type_map['Ptr'], (0, name_type_map['NiAVObject']), (False, None), (None, None)
		yield 'data', name_type_map['Ref'], (0, name_type_map['BSSkinBoneData']), (False, None), (None, None)
		yield 'num_bones', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'bones', Array, (0, name_type_map['NiNode'], (None,), name_type_map['Ptr']), (False, None), (None, None)
		yield 'num_scales', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'scales', Array, (0, None, (None,), name_type_map['Vector3']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'skeleton_root', name_type_map['Ptr'], (0, name_type_map['NiAVObject']), (False, None)
		yield 'data', name_type_map['Ref'], (0, name_type_map['BSSkinBoneData']), (False, None)
		yield 'num_bones', name_type_map['Uint'], (0, None), (False, None)
		yield 'bones', Array, (0, name_type_map['NiNode'], (instance.num_bones,), name_type_map['Ptr']), (False, None)
		yield 'num_scales', name_type_map['Uint'], (0, None), (False, None)
		yield 'scales', Array, (0, None, (instance.num_scales,), name_type_map['Vector3']), (False, None)

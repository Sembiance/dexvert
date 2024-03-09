from nifgen.array import Array
from nifgen.base_struct import BaseStruct
from nifgen.formats.nif.imports import name_type_map


class BonePose(BaseStruct):

	"""
	A list of transforms for each bone in bhkPoseArray.
	"""

	__name__ = 'BonePose'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.num_transforms = name_type_map['Uint'](self.context, 0, None)
		self.transforms = Array(self.context, 0, None, (0,), name_type_map['BoneTransform'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'num_transforms', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'transforms', Array, (0, None, (None,), name_type_map['BoneTransform']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'num_transforms', name_type_map['Uint'], (0, None), (False, None)
		yield 'transforms', Array, (0, None, (instance.num_transforms,), name_type_map['BoneTransform']), (False, None)

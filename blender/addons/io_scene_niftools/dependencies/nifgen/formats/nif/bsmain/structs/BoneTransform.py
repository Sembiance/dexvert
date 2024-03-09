from nifgen.base_struct import BaseStruct
from nifgen.formats.nif.imports import name_type_map


class BoneTransform(BaseStruct):

	"""
	Transformation data for the bone at this index in bhkPoseArray.
	"""

	__name__ = 'BoneTransform'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.translation = name_type_map['Vector3'](self.context, 0, None)
		self.rotation = name_type_map['HkQuaternion'](self.context, 0, None)
		self.scale = name_type_map['Vector3'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'translation', name_type_map['Vector3'], (0, None), (False, None), (None, None)
		yield 'rotation', name_type_map['HkQuaternion'], (0, None), (False, None), (None, None)
		yield 'scale', name_type_map['Vector3'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'translation', name_type_map['Vector3'], (0, None), (False, None)
		yield 'rotation', name_type_map['HkQuaternion'], (0, None), (False, None)
		yield 'scale', name_type_map['Vector3'], (0, None), (False, None)

from nifgen.base_struct import BaseStruct
from nifgen.formats.ms2.imports import name_type_map


class IKTarget(BaseStruct):

	"""
	2 bytes
	"""

	__name__ = 'IKTarget'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.ik_blend = name_type_map['BonePointer'](self.context, 0, None)
		self.ik_end = name_type_map['BonePointer'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'ik_blend', name_type_map['BonePointer'], (0, None), (False, None), (None, None)
		yield 'ik_end', name_type_map['BonePointer'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'ik_blend', name_type_map['BonePointer'], (0, None), (False, None)
		yield 'ik_end', name_type_map['BonePointer'], (0, None), (False, None)

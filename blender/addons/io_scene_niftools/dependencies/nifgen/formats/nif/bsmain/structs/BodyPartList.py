from nifgen.base_struct import BaseStruct
from nifgen.formats.nif.imports import name_type_map


class BodyPartList(BaseStruct):

	"""
	Body part list for DismemberSkinInstance
	"""

	__name__ = 'BodyPartList'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# Flags related to the Body Partition
		self.part_flag = name_type_map['BSPartFlag'].from_value(257)

		# Body Part Index
		self.body_part = name_type_map['BSDismemberBodyPartType'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'part_flag', name_type_map['BSPartFlag'], (0, None), (False, 257), (None, None)
		yield 'body_part', name_type_map['BSDismemberBodyPartType'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'part_flag', name_type_map['BSPartFlag'], (0, None), (False, 257)
		yield 'body_part', name_type_map['BSDismemberBodyPartType'], (0, None), (False, None)

from nifgen.base_struct import BaseStruct
from nifgen.formats.nif.imports import name_type_map


class NiAGDDataBlocks(BaseStruct):

	__name__ = 'NiAGDDataBlocks'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.has_data = name_type_map['Bool'](self.context, 0, None)
		self.data_block = name_type_map['NiAGDDataBlock'](self.context, self.arg, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'has_data', name_type_map['Bool'], (0, None), (False, None), (None, None)
		yield 'data_block', name_type_map['NiAGDDataBlock'], (None, None), (False, None), (None, True)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'has_data', name_type_map['Bool'], (0, None), (False, None)
		if instance.has_data:
			yield 'data_block', name_type_map['NiAGDDataBlock'], (instance.arg, None), (False, None)

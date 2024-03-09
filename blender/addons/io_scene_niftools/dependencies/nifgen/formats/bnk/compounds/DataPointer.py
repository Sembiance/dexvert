from nifgen.base_struct import BaseStruct
from nifgen.formats.bnk.imports import name_type_map


class DataPointer(BaseStruct):

	"""
	second Section of a soundbank aux
	"""

	__name__ = 'DataPointer'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.wem_id = name_type_map['Uint'](self.context, 0, None)

		# offset into data section
		self.data_section_offset = name_type_map['Uint'](self.context, 0, None)

		# length of the wem file
		self.wem_filesize = name_type_map['Uint'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'wem_id', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'data_section_offset', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'wem_filesize', name_type_map['Uint'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'wem_id', name_type_map['Uint'], (0, None), (False, None)
		yield 'data_section_offset', name_type_map['Uint'], (0, None), (False, None)
		yield 'wem_filesize', name_type_map['Uint'], (0, None), (False, None)

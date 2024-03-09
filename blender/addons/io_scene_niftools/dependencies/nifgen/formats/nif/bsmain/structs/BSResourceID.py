from nifgen.array import Array
from nifgen.base_struct import BaseStruct
from nifgen.formats.nif.imports import name_type_map


class BSResourceID(BaseStruct):

	__name__ = 'BSResourceID'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.file_hash = name_type_map['Uint'](self.context, 0, None)
		self.extension = Array(self.context, 0, None, (0,), name_type_map['Char'])
		self.directory_hash = name_type_map['Uint'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'file_hash', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'extension', Array, (0, None, (4,), name_type_map['Char']), (False, None), (None, None)
		yield 'directory_hash', name_type_map['Uint'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'file_hash', name_type_map['Uint'], (0, None), (False, None)
		yield 'extension', Array, (0, None, (4,), name_type_map['Char']), (False, None)
		yield 'directory_hash', name_type_map['Uint'], (0, None), (False, None)

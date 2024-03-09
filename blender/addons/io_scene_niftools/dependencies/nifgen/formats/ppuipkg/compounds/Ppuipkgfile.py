from nifgen.formats.ovl_base.compounds.MemStruct import MemStruct
from nifgen.formats.ppuipkg.imports import name_type_map


class Ppuipkgfile(MemStruct):

	__name__ = 'ppuipkgfile'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.file_size = name_type_map['Uint64'](self.context, 0, None)
		self.file_name = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		self.file_content = name_type_map['ArrayPointer'](self.context, self.file_size, name_type_map['Char'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'file_name', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'file_size', name_type_map['Uint64'], (0, None), (False, None), (None, None)
		yield 'file_content', name_type_map['ArrayPointer'], (None, name_type_map['Char']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'file_name', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'file_size', name_type_map['Uint64'], (0, None), (False, None)
		yield 'file_content', name_type_map['ArrayPointer'], (instance.file_size, name_type_map['Char']), (False, None)

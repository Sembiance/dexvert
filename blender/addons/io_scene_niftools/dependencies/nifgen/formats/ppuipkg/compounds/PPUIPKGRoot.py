from nifgen.formats.ovl_base.compounds.MemStruct import MemStruct
from nifgen.formats.ppuipkg.imports import name_type_map


class PPUIPKGRoot(MemStruct):

	__name__ = 'PPUIPKGRoot'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.file_count = name_type_map['Uint64'](self.context, 0, None)
		self.icondata_count = name_type_map['Uint64'](self.context, 0, None)
		self.basic_path = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		self.files = name_type_map['ArrayPointer'](self.context, self.file_count, name_type_map['Ppuipkgfile'])
		self.types = name_type_map['ArrayPointer'](self.context, self.icondata_count, name_type_map['UserInterfaceIconData'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'basic_path', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'file_count', name_type_map['Uint64'], (0, None), (False, None), (None, None)
		yield 'files', name_type_map['ArrayPointer'], (None, name_type_map['Ppuipkgfile']), (False, None), (None, None)
		yield 'icondata_count', name_type_map['Uint64'], (0, None), (False, None), (None, None)
		yield 'types', name_type_map['ArrayPointer'], (None, name_type_map['UserInterfaceIconData']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'basic_path', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'file_count', name_type_map['Uint64'], (0, None), (False, None)
		yield 'files', name_type_map['ArrayPointer'], (instance.file_count, name_type_map['Ppuipkgfile']), (False, None)
		yield 'icondata_count', name_type_map['Uint64'], (0, None), (False, None)
		yield 'types', name_type_map['ArrayPointer'], (instance.icondata_count, name_type_map['UserInterfaceIconData']), (False, None)

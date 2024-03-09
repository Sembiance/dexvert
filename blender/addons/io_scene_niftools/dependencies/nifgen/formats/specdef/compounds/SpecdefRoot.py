from nifgen.formats.ovl_base.compounds.MemStruct import MemStruct
from nifgen.formats.specdef.imports import name_type_map


class SpecdefRoot(MemStruct):

	__name__ = 'SpecdefRoot'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.attrib_count = name_type_map['Ushort'](self.context, 0, None)
		self.flags = name_type_map['Ushort'](self.context, 0, None)
		self.name_count = name_type_map['Ubyte'](self.context, 0, None)
		self.childspec_count = name_type_map['Ubyte'](self.context, 0, None)
		self.manager_count = name_type_map['Ubyte'](self.context, 0, None)
		self.script_count = name_type_map['Ubyte'](self.context, 0, None)
		self.attribs = name_type_map['ArrayPointer'](self.context, self.attrib_count, name_type_map['Spec'])
		self.name_foreach_attribs = name_type_map['ForEachPointer'](self.context, self.attribs, name_type_map['NamePtr'])
		self.data_foreach_attribs = name_type_map['ForEachPointer'](self.context, self.attribs, name_type_map['DataPtr'])
		self.names = name_type_map['Pointer'](self.context, self.name_count, name_type_map['ZStringList'])
		self.childspecs = name_type_map['Pointer'](self.context, self.childspec_count, name_type_map['ZStringList'])
		self.managers = name_type_map['Pointer'](self.context, self.manager_count, name_type_map['ZStringList'])
		self.scripts = name_type_map['Pointer'](self.context, self.script_count, name_type_map['ZStringList'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'attrib_count', name_type_map['Ushort'], (0, None), (False, None), (None, None)
		yield 'flags', name_type_map['Ushort'], (0, None), (False, None), (None, None)
		yield 'name_count', name_type_map['Ubyte'], (0, None), (False, None), (None, None)
		yield 'childspec_count', name_type_map['Ubyte'], (0, None), (False, None), (None, None)
		yield 'manager_count', name_type_map['Ubyte'], (0, None), (False, None), (None, None)
		yield 'script_count', name_type_map['Ubyte'], (0, None), (False, None), (None, None)
		yield 'attribs', name_type_map['ArrayPointer'], (None, name_type_map['Spec']), (False, None), (None, None)
		yield 'name_foreach_attribs', name_type_map['ForEachPointer'], (None, name_type_map['NamePtr']), (False, None), (None, None)
		yield 'data_foreach_attribs', name_type_map['ForEachPointer'], (None, name_type_map['DataPtr']), (False, None), (None, None)
		yield 'names', name_type_map['Pointer'], (None, name_type_map['ZStringList']), (False, None), (None, None)
		yield 'childspecs', name_type_map['Pointer'], (None, name_type_map['ZStringList']), (False, None), (None, None)
		yield 'managers', name_type_map['Pointer'], (None, name_type_map['ZStringList']), (False, None), (None, None)
		yield 'scripts', name_type_map['Pointer'], (None, name_type_map['ZStringList']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'attrib_count', name_type_map['Ushort'], (0, None), (False, None)
		yield 'flags', name_type_map['Ushort'], (0, None), (False, None)
		yield 'name_count', name_type_map['Ubyte'], (0, None), (False, None)
		yield 'childspec_count', name_type_map['Ubyte'], (0, None), (False, None)
		yield 'manager_count', name_type_map['Ubyte'], (0, None), (False, None)
		yield 'script_count', name_type_map['Ubyte'], (0, None), (False, None)
		yield 'attribs', name_type_map['ArrayPointer'], (instance.attrib_count, name_type_map['Spec']), (False, None)
		yield 'name_foreach_attribs', name_type_map['ForEachPointer'], (instance.attribs, name_type_map['NamePtr']), (False, None)
		yield 'data_foreach_attribs', name_type_map['ForEachPointer'], (instance.attribs, name_type_map['DataPtr']), (False, None)
		yield 'names', name_type_map['Pointer'], (instance.name_count, name_type_map['ZStringList']), (False, None)
		yield 'childspecs', name_type_map['Pointer'], (instance.childspec_count, name_type_map['ZStringList']), (False, None)
		yield 'managers', name_type_map['Pointer'], (instance.manager_count, name_type_map['ZStringList']), (False, None)
		yield 'scripts', name_type_map['Pointer'], (instance.script_count, name_type_map['ZStringList']), (False, None)

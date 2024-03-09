from nifgen.formats.enumnamer.imports import name_type_map
from nifgen.formats.ovl_base.compounds.MemStruct import MemStruct


class EnumnamerRoot(MemStruct):

	__name__ = 'EnumnamerRoot'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.count = name_type_map['Uint64'](self.context, 0, None)
		self.strings = name_type_map['Pointer'](self.context, self.count, name_type_map['ZStringList'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'count', name_type_map['Uint64'], (0, None), (False, None), (None, None)
		yield 'strings', name_type_map['Pointer'], (None, name_type_map['ZStringList']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'count', name_type_map['Uint64'], (0, None), (False, None)
		yield 'strings', name_type_map['Pointer'], (instance.count, name_type_map['ZStringList']), (False, None)

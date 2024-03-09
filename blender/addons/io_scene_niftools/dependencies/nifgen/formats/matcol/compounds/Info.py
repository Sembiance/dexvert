from nifgen.array import Array
from nifgen.formats.matcol.imports import name_type_map
from nifgen.formats.ovl_base.compounds.MemStruct import MemStruct


class Info(MemStruct):

	__name__ = 'Info'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.flags = Array(self.context, 0, None, (0,), name_type_map['Byte'])
		self.value = Array(self.context, 0, None, (0,), name_type_map['Float'])
		self.padding = name_type_map['Uint'](self.context, 0, None)
		self.info_name = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'info_name', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'flags', Array, (0, None, (4,), name_type_map['Byte']), (False, None), (None, None)
		yield 'value', Array, (0, None, (4,), name_type_map['Float']), (False, None), (None, None)
		yield 'padding', name_type_map['Uint'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'info_name', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'flags', Array, (0, None, (4,), name_type_map['Byte']), (False, None)
		yield 'value', Array, (0, None, (4,), name_type_map['Float']), (False, None)
		yield 'padding', name_type_map['Uint'], (0, None), (False, None)

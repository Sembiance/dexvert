from nifgen.formats.ovl_base.compounds.MemStruct import MemStruct
from nifgen.formats.path.imports import name_type_map


class SubBrace(MemStruct):

	__name__ = 'SubBrace'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.brace_model_1 = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		self.brace_model_2 = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		self.brace_model_3 = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		self.brace_model_4 = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'brace_model_1', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'brace_model_2', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'brace_model_3', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'brace_model_4', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'brace_model_1', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'brace_model_2', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'brace_model_3', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'brace_model_4', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)

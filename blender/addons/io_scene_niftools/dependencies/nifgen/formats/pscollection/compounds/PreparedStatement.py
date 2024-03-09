from nifgen.formats.ovl_base.compounds.MemStruct import MemStruct
from nifgen.formats.pscollection.imports import name_type_map


class PreparedStatement(MemStruct):

	__name__ = 'PreparedStatement'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.arg_count = name_type_map['Uint64'].from_value(0)
		self.args = name_type_map['ArrayPointer'](self.context, self.arg_count, name_type_map['Arg'])
		self.statement_name = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		self.sql_query = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'args', name_type_map['ArrayPointer'], (None, name_type_map['Arg']), (False, None), (None, None)
		yield 'arg_count', name_type_map['Uint64'], (0, None), (True, 0), (None, None)
		yield 'statement_name', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'sql_query', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'args', name_type_map['ArrayPointer'], (instance.arg_count, name_type_map['Arg']), (False, None)
		yield 'arg_count', name_type_map['Uint64'], (0, None), (True, 0)
		yield 'statement_name', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'sql_query', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)

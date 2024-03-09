from nifgen.formats.ovl_base.compounds.MemStruct import MemStruct
from nifgen.formats.pscollection.imports import name_type_map


class Arg(MemStruct):

	__name__ = 'Arg'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.u_0 = name_type_map['Ubyte'].from_value(0)
		self.arg_type = name_type_map['Ubyte'](self.context, 0, None)

		# one-based index
		self.arg_index = name_type_map['Ubyte'](self.context, 0, None)
		self.u_1 = name_type_map['Ubyte'].from_value(0)
		self.u_2 = name_type_map['Uint'].from_value(0)
		self.u_4 = name_type_map['Uint64'].from_value(0)
		self.arg_name = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'u_0', name_type_map['Ubyte'], (0, None), (True, 0), (None, None)
		yield 'arg_type', name_type_map['Ubyte'], (0, None), (False, None), (None, None)
		yield 'arg_index', name_type_map['Ubyte'], (0, None), (False, None), (None, None)
		yield 'u_1', name_type_map['Ubyte'], (0, None), (True, 0), (None, None)
		yield 'u_2', name_type_map['Uint'], (0, None), (True, 0), (None, None)
		yield 'arg_name', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'u_4', name_type_map['Uint64'], (0, None), (True, 0), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'u_0', name_type_map['Ubyte'], (0, None), (True, 0)
		yield 'arg_type', name_type_map['Ubyte'], (0, None), (False, None)
		yield 'arg_index', name_type_map['Ubyte'], (0, None), (False, None)
		yield 'u_1', name_type_map['Ubyte'], (0, None), (True, 0)
		yield 'u_2', name_type_map['Uint'], (0, None), (True, 0)
		yield 'arg_name', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'u_4', name_type_map['Uint64'], (0, None), (True, 0)

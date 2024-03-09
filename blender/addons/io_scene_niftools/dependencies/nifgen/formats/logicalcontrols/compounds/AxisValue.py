from nifgen.formats.logicalcontrols.imports import name_type_map
from nifgen.formats.ovl_base.compounds.MemStruct import MemStruct


class AxisValue(MemStruct):

	__name__ = 'AxisValue'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.u_0 = name_type_map['Uint64'](self.context, 0, None)
		self.u_1 = name_type_map['Uint64'](self.context, 0, None)
		self.u_2 = name_type_map['Uint64'](self.context, 0, None)
		self.u_3 = name_type_map['Uint64'](self.context, 0, None)
		self.u_4 = name_type_map['Uint64'](self.context, 0, None)
		self.axis_name = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		self.value_name = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'axis_name', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'u_0', name_type_map['Uint64'], (0, None), (False, None), (None, None)
		yield 'u_1', name_type_map['Uint64'], (0, None), (False, None), (None, None)
		yield 'u_2', name_type_map['Uint64'], (0, None), (False, None), (None, None)
		yield 'value_name', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'u_3', name_type_map['Uint64'], (0, None), (False, None), (None, None)
		yield 'u_4', name_type_map['Uint64'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'axis_name', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'u_0', name_type_map['Uint64'], (0, None), (False, None)
		yield 'u_1', name_type_map['Uint64'], (0, None), (False, None)
		yield 'u_2', name_type_map['Uint64'], (0, None), (False, None)
		yield 'value_name', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'u_3', name_type_map['Uint64'], (0, None), (False, None)
		yield 'u_4', name_type_map['Uint64'], (0, None), (False, None)

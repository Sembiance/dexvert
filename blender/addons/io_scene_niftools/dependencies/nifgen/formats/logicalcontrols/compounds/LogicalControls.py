from nifgen.formats.logicalcontrols.imports import name_type_map
from nifgen.formats.ovl_base.compounds.MemStruct import MemStruct


class LogicalControls(MemStruct):

	__name__ = 'LogicalControls'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.button_count = name_type_map['Ubyte'](self.context, 0, None)
		self.axis_count = name_type_map['Ubyte'](self.context, 0, None)
		self.count_3 = name_type_map['Ubyte'](self.context, 0, None)
		self.count_4 = name_type_map['Ubyte'](self.context, 0, None)
		self.flags = name_type_map['Uint'](self.context, 0, None)
		self.buttons = name_type_map['ArrayPointer'](self.context, self.button_count, name_type_map['Button'])
		self.axes = name_type_map['ArrayPointer'](self.context, self.axis_count, name_type_map['AxisValue'])
		self.axis_buttons = name_type_map['ArrayPointer'](self.context, self.count_3, name_type_map['AxisButton'])
		self.d = name_type_map['ArrayPointer'](self.context, self.count_4, name_type_map['Some'])
		self.unsure = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'buttons', name_type_map['ArrayPointer'], (None, name_type_map['Button']), (False, None), (None, None)
		yield 'axes', name_type_map['ArrayPointer'], (None, name_type_map['AxisValue']), (False, None), (None, None)
		yield 'axis_buttons', name_type_map['ArrayPointer'], (None, name_type_map['AxisButton']), (False, None), (None, None)
		yield 'd', name_type_map['ArrayPointer'], (None, name_type_map['Some']), (False, None), (None, None)
		yield 'button_count', name_type_map['Ubyte'], (0, None), (False, None), (None, None)
		yield 'axis_count', name_type_map['Ubyte'], (0, None), (False, None), (None, None)
		yield 'count_3', name_type_map['Ubyte'], (0, None), (False, None), (None, None)
		yield 'count_4', name_type_map['Ubyte'], (0, None), (False, None), (None, None)
		yield 'flags', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'unsure', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'buttons', name_type_map['ArrayPointer'], (instance.button_count, name_type_map['Button']), (False, None)
		yield 'axes', name_type_map['ArrayPointer'], (instance.axis_count, name_type_map['AxisValue']), (False, None)
		yield 'axis_buttons', name_type_map['ArrayPointer'], (instance.count_3, name_type_map['AxisButton']), (False, None)
		yield 'd', name_type_map['ArrayPointer'], (instance.count_4, name_type_map['Some']), (False, None)
		yield 'button_count', name_type_map['Ubyte'], (0, None), (False, None)
		yield 'axis_count', name_type_map['Ubyte'], (0, None), (False, None)
		yield 'count_3', name_type_map['Ubyte'], (0, None), (False, None)
		yield 'count_4', name_type_map['Ubyte'], (0, None), (False, None)
		yield 'flags', name_type_map['Uint'], (0, None), (False, None)
		yield 'unsure', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)

from nifgen.formats.logicalcontrols.imports import name_type_map
from nifgen.formats.ovl_base.compounds.MemStruct import MemStruct


class AxisButton(MemStruct):

	"""
	24 bytes, can be padded to 32
	"""

	__name__ = 'AxisButton'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.button_name = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		self.axis_name_x = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		self.axis_name_y = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'button_name', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'axis_name_x', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'axis_name_y', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'button_name', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'axis_name_x', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'axis_name_y', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)

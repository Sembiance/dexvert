from nifgen.formats.logicalcontrols.imports import name_type_map
from nifgen.formats.ovl_base.compounds.MemStruct import MemStruct


class Some(MemStruct):

	"""
	24 bytes
	"""

	__name__ = 'Some'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.some_count = name_type_map['Uint64'](self.context, 0, None)
		self.some_name = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		self.some_data = name_type_map['ArrayPointer'](self.context, self.some_count, name_type_map['SomeData'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'some_name', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'some_data', name_type_map['ArrayPointer'], (None, name_type_map['SomeData']), (False, None), (None, None)
		yield 'some_count', name_type_map['Uint64'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'some_name', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'some_data', name_type_map['ArrayPointer'], (instance.some_count, name_type_map['SomeData']), (False, None)
		yield 'some_count', name_type_map['Uint64'], (0, None), (False, None)

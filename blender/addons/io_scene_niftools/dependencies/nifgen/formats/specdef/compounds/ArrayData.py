from nifgen.formats.ovl_base.compounds.MemStruct import MemStruct
from nifgen.formats.specdef.imports import name_type_map


class ArrayData(MemStruct):

	"""
	16 bytes in log
	"""

	__name__ = 'ArrayData'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.dtype = name_type_map['SpecdefDtype'](self.context, 0, None)
		self.unused = name_type_map['Uint'](self.context, 0, None)
		self.item = name_type_map['Pointer'](self.context, self.dtype, name_type_map['Data'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'item', name_type_map['Pointer'], (None, name_type_map['Data']), (False, None), (None, None)
		yield 'dtype', name_type_map['SpecdefDtype'], (0, None), (False, None), (None, None)
		yield 'unused', name_type_map['Uint'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'item', name_type_map['Pointer'], (instance.dtype, name_type_map['Data']), (False, None)
		yield 'dtype', name_type_map['SpecdefDtype'], (0, None), (False, None)
		yield 'unused', name_type_map['Uint'], (0, None), (False, None)

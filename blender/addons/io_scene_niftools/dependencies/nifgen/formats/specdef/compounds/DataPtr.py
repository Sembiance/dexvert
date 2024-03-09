from nifgen.formats.ovl_base.compounds.MemStruct import MemStruct
from nifgen.formats.specdef.imports import name_type_map


class DataPtr(MemStruct):

	"""
	#ARG# is dtype
	"""

	__name__ = 'DataPtr'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.data_ptr = name_type_map['Pointer'](self.context, self.arg.dtype, name_type_map['Data'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'data_ptr', name_type_map['Pointer'], (None, name_type_map['Data']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'data_ptr', name_type_map['Pointer'], (instance.arg.dtype, name_type_map['Data']), (False, None)

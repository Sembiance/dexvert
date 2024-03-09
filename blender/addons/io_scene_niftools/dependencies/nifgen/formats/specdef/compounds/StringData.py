from nifgen.formats.ovl_base.compounds.MemStruct import MemStruct
from nifgen.formats.specdef.imports import name_type_map


class StringData(MemStruct):

	"""
	16 bytes in log
	"""

	__name__ = 'StringData'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.ioptional = name_type_map['Uint'](self.context, 0, None)
		self.str_name = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'str_name', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'ioptional', name_type_map['Uint'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'str_name', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'ioptional', name_type_map['Uint'], (0, None), (False, None)

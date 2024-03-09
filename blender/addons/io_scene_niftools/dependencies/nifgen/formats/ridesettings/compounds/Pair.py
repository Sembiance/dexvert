from nifgen.formats.ovl_base.compounds.MemStruct import MemStruct
from nifgen.formats.ridesettings.imports import name_type_map


class Pair(MemStruct):

	__name__ = 'Pair'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.value_0 = name_type_map['Uint'](self.context, 0, None)
		self.value_1 = name_type_map['Float'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'value_0', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'value_1', name_type_map['Float'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'value_0', name_type_map['Uint'], (0, None), (False, None)
		yield 'value_1', name_type_map['Float'], (0, None), (False, None)

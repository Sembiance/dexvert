from nifgen.formats.ovl_base.compounds.MemStruct import MemStruct
from nifgen.formats.path.imports import name_type_map


class SupportSetData(MemStruct):

	__name__ = 'SupportSetData'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.unk_index = name_type_map['Uint'](self.context, 0, None)
		self.unk_int_1 = name_type_map['Uint'](self.context, 0, None)
		self.unk_int_2 = name_type_map['Uint'](self.context, 0, None)
		self.unk_float_1 = name_type_map['Float'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'unk_index', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'unk_int_1', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'unk_int_2', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'unk_float_1', name_type_map['Float'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'unk_index', name_type_map['Uint'], (0, None), (False, None)
		yield 'unk_int_1', name_type_map['Uint'], (0, None), (False, None)
		yield 'unk_int_2', name_type_map['Uint'], (0, None), (False, None)
		yield 'unk_float_1', name_type_map['Float'], (0, None), (False, None)

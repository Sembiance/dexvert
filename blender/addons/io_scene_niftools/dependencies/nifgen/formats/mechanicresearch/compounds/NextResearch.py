from nifgen.array import Array
from nifgen.formats.mechanicresearch.imports import name_type_map
from nifgen.formats.ovl_base.compounds.MemStruct import MemStruct


class NextResearch(MemStruct):

	__name__ = 'NextResearch'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.unk_1 = name_type_map['Uint64'](self.context, 0, None)
		self.item_name = Array(self.context, 0, name_type_map['ZString'], (0,), name_type_map['Pointer'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'item_name', Array, (0, name_type_map['ZString'], (None,), name_type_map['Pointer']), (False, None), (None, None)
		yield 'unk_1', name_type_map['Uint64'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'item_name', Array, (0, name_type_map['ZString'], (instance.arg,), name_type_map['Pointer']), (False, None)
		yield 'unk_1', name_type_map['Uint64'], (0, None), (False, None)

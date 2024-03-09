from nifgen.formats.frendercontextset.imports import name_type_map
from nifgen.formats.ovl_base.compounds.MemStruct import MemStruct


class ContextSet1SubItem(MemStruct):

	__name__ = 'ContextSet1SubItem'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.stuff_1_sub_order_or_flags = name_type_map['Uint64'](self.context, 0, None)
		self.stuff_1_sub_name = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'stuff_1_sub_name', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'stuff_1_sub_order_or_flags', name_type_map['Uint64'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'stuff_1_sub_name', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'stuff_1_sub_order_or_flags', name_type_map['Uint64'], (0, None), (False, None)

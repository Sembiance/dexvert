from nifgen.formats.frendercontextset.imports import name_type_map
from nifgen.formats.ovl_base.compounds.MemStruct import MemStruct


class FRenderContextSetRoot(MemStruct):

	__name__ = 'FRenderContextSetRoot'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.ptr_1_count = name_type_map['Uint64'](self.context, 0, None)
		self.ptr_2_count = name_type_map['Uint64'](self.context, 0, None)
		self.ptr_3_count = name_type_map['Uint64'](self.context, 0, None)
		self.ptr_1_list = name_type_map['ArrayPointer'](self.context, self.ptr_1_count, name_type_map['ContextSet1Item'])
		self.ptr_2_list = name_type_map['ArrayPointer'](self.context, self.ptr_2_count, name_type_map['ContextSet2Item'])
		self.ptr_3_list = name_type_map['ArrayPointer'](self.context, self.ptr_3_count, name_type_map['ContextSet3Item'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'ptr_1_list', name_type_map['ArrayPointer'], (None, name_type_map['ContextSet1Item']), (False, None), (None, None)
		yield 'ptr_1_count', name_type_map['Uint64'], (0, None), (False, None), (None, None)
		yield 'ptr_2_list', name_type_map['ArrayPointer'], (None, name_type_map['ContextSet2Item']), (False, None), (None, None)
		yield 'ptr_2_count', name_type_map['Uint64'], (0, None), (False, None), (None, None)
		yield 'ptr_3_list', name_type_map['ArrayPointer'], (None, name_type_map['ContextSet3Item']), (False, None), (None, None)
		yield 'ptr_3_count', name_type_map['Uint64'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'ptr_1_list', name_type_map['ArrayPointer'], (instance.ptr_1_count, name_type_map['ContextSet1Item']), (False, None)
		yield 'ptr_1_count', name_type_map['Uint64'], (0, None), (False, None)
		yield 'ptr_2_list', name_type_map['ArrayPointer'], (instance.ptr_2_count, name_type_map['ContextSet2Item']), (False, None)
		yield 'ptr_2_count', name_type_map['Uint64'], (0, None), (False, None)
		yield 'ptr_3_list', name_type_map['ArrayPointer'], (instance.ptr_3_count, name_type_map['ContextSet3Item']), (False, None)
		yield 'ptr_3_count', name_type_map['Uint64'], (0, None), (False, None)

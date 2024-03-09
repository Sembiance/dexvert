from nifgen.formats.buildingset.imports import name_type_map
from nifgen.formats.ovl_base.compounds.MemStruct import MemStruct


class BuildingSetRoot(MemStruct):

	__name__ = 'BuildingSetRoot'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.set_count_or_type = name_type_map['Uint64'](self.context, 0, None)
		self.unk_1_found_as_0 = name_type_map['Uint64'](self.context, 0, None)
		self.unk_2_found_as_0 = name_type_map['Uint64'](self.context, 0, None)
		self.set_id_name = name_type_map['Pointer'](self.context, 0, name_type_map['ZStringObfuscated'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'set_id_name', name_type_map['Pointer'], (0, name_type_map['ZStringObfuscated']), (False, None), (None, None)
		yield 'set_count_or_type', name_type_map['Uint64'], (0, None), (False, None), (None, None)
		yield 'unk_1_found_as_0', name_type_map['Uint64'], (0, None), (False, None), (None, None)
		yield 'unk_2_found_as_0', name_type_map['Uint64'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'set_id_name', name_type_map['Pointer'], (0, name_type_map['ZStringObfuscated']), (False, None)
		yield 'set_count_or_type', name_type_map['Uint64'], (0, None), (False, None)
		yield 'unk_1_found_as_0', name_type_map['Uint64'], (0, None), (False, None)
		yield 'unk_2_found_as_0', name_type_map['Uint64'], (0, None), (False, None)

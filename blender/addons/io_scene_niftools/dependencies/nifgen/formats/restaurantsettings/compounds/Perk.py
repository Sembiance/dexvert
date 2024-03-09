from nifgen.formats.ovl_base.compounds.MemStruct import MemStruct
from nifgen.formats.restaurantsettings.imports import name_type_map


class Perk(MemStruct):

	__name__ = 'Perk'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.unk_0 = name_type_map['Uint64'](self.context, 0, None)
		self.building_cost = name_type_map['Uint64'](self.context, 0, None)
		self.running_cost_base = name_type_map['Uint64'](self.context, 0, None)
		self.running_cost_per_extension = name_type_map['Uint64'](self.context, 0, None)
		self.unk_4 = name_type_map['Float'](self.context, 0, None)
		self.unk_5 = name_type_map['Float'](self.context, 0, None)
		self.unk_6 = name_type_map['Float'](self.context, 0, None)
		self.appeal_adults = name_type_map['Float'](self.context, 0, None)
		self.appeal_families = name_type_map['Float'](self.context, 0, None)
		self.appeal_teenagers = name_type_map['Float'](self.context, 0, None)
		self.label = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		self.desc = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		self.icon = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'unk_0', name_type_map['Uint64'], (0, None), (False, None), (None, None)
		yield 'building_cost', name_type_map['Uint64'], (0, None), (False, None), (None, None)
		yield 'running_cost_base', name_type_map['Uint64'], (0, None), (False, None), (None, None)
		yield 'running_cost_per_extension', name_type_map['Uint64'], (0, None), (False, None), (None, None)
		yield 'unk_4', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'unk_5', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'label', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'desc', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'icon', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'unk_6', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'appeal_adults', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'appeal_families', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'appeal_teenagers', name_type_map['Float'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'unk_0', name_type_map['Uint64'], (0, None), (False, None)
		yield 'building_cost', name_type_map['Uint64'], (0, None), (False, None)
		yield 'running_cost_base', name_type_map['Uint64'], (0, None), (False, None)
		yield 'running_cost_per_extension', name_type_map['Uint64'], (0, None), (False, None)
		yield 'unk_4', name_type_map['Float'], (0, None), (False, None)
		yield 'unk_5', name_type_map['Float'], (0, None), (False, None)
		yield 'label', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'desc', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'icon', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'unk_6', name_type_map['Float'], (0, None), (False, None)
		yield 'appeal_adults', name_type_map['Float'], (0, None), (False, None)
		yield 'appeal_families', name_type_map['Float'], (0, None), (False, None)
		yield 'appeal_teenagers', name_type_map['Float'], (0, None), (False, None)

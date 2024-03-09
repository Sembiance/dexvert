from nifgen.formats.ovl_base.compounds.MemStruct import MemStruct
from nifgen.formats.restaurantsettings.imports import name_type_map


class RestaurantSettingsRoot(MemStruct):

	__name__ = 'RestaurantSettingsRoot'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.running_cost_base = name_type_map['Uint64'](self.context, 0, None)
		self.unk_1 = name_type_map['Uint'](self.context, 0, None)
		self.unk_2 = name_type_map['Float'](self.context, 0, None)
		self.unk_3 = name_type_map['Float'](self.context, 0, None)
		self.unk_4 = name_type_map['Float'](self.context, 0, None)
		self.unk_5 = name_type_map['Float'](self.context, 0, None)
		self.unk_6 = name_type_map['Float'](self.context, 0, None)
		self.running_cost_per_extension = name_type_map['Uint64'](self.context, 0, None)
		self.unk_8 = name_type_map['Uint'](self.context, 0, None)
		self.unk_9 = name_type_map['Float'](self.context, 0, None)
		self.count = name_type_map['Uint64'](self.context, 0, None)
		self.perks = name_type_map['ArrayPointer'](self.context, self.count, name_type_map['Perk'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'running_cost_base', name_type_map['Uint64'], (0, None), (False, None), (None, None)
		yield 'unk_1', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'unk_2', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'unk_3', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'unk_4', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'unk_5', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'unk_6', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'running_cost_per_extension', name_type_map['Uint64'], (0, None), (False, None), (None, None)
		yield 'unk_8', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'unk_9', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'perks', name_type_map['ArrayPointer'], (None, name_type_map['Perk']), (False, None), (None, None)
		yield 'count', name_type_map['Uint64'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'running_cost_base', name_type_map['Uint64'], (0, None), (False, None)
		yield 'unk_1', name_type_map['Uint'], (0, None), (False, None)
		yield 'unk_2', name_type_map['Float'], (0, None), (False, None)
		yield 'unk_3', name_type_map['Float'], (0, None), (False, None)
		yield 'unk_4', name_type_map['Float'], (0, None), (False, None)
		yield 'unk_5', name_type_map['Float'], (0, None), (False, None)
		yield 'unk_6', name_type_map['Float'], (0, None), (False, None)
		yield 'running_cost_per_extension', name_type_map['Uint64'], (0, None), (False, None)
		yield 'unk_8', name_type_map['Uint'], (0, None), (False, None)
		yield 'unk_9', name_type_map['Float'], (0, None), (False, None)
		yield 'perks', name_type_map['ArrayPointer'], (instance.count, name_type_map['Perk']), (False, None)
		yield 'count', name_type_map['Uint64'], (0, None), (False, None)

from nifgen.formats.ovl_base.compounds.MemStruct import MemStruct
from nifgen.formats.wmeta.imports import name_type_map


class Jwe2WmetasbMain(MemStruct):

	__name__ = 'JWE2WmetasbMain'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.events_count = name_type_map['Uint'](self.context, 0, None)
		self.hash = name_type_map['Uint'](self.context, 0, None)
		self.unk_1 = name_type_map['Uint'](self.context, 0, None)
		self.unk_2 = name_type_map['Uint'](self.context, 0, None)
		self.block_name = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		self.events = name_type_map['ArrayPointer'](self.context, self.events_count, name_type_map['EventEntry'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'block_name', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'events', name_type_map['ArrayPointer'], (None, name_type_map['EventEntry']), (False, None), (None, None)
		yield 'events_count', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'hash', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'unk_1', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'unk_2', name_type_map['Uint'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'block_name', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'events', name_type_map['ArrayPointer'], (instance.events_count, name_type_map['EventEntry']), (False, None)
		yield 'events_count', name_type_map['Uint'], (0, None), (False, None)
		yield 'hash', name_type_map['Uint'], (0, None), (False, None)
		yield 'unk_1', name_type_map['Uint'], (0, None), (False, None)
		yield 'unk_2', name_type_map['Uint'], (0, None), (False, None)

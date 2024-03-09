from nifgen.formats.cinematic.imports import name_type_map
from nifgen.formats.ovl_base.compounds.MemStruct import MemStruct


class State(MemStruct):

	"""
	JWE2: 64 bytes
	"""

	__name__ = 'State'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.a = name_type_map['Uint64'](self.context, 0, None)
		self.b = name_type_map['Uint64'](self.context, 0, None)
		self.c = name_type_map['Uint64'](self.context, 0, None)
		self.d = name_type_map['Uint64'](self.context, 0, None)
		self.abstract_name = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		self.concrete_name = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		self.prefab_name = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		self.events_list = name_type_map['Pointer'](self.context, 0, name_type_map['EventsList'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'abstract_name', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'concrete_name', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'prefab_name', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'a', name_type_map['Uint64'], (0, None), (False, None), (None, None)
		yield 'b', name_type_map['Uint64'], (0, None), (False, None), (None, None)
		yield 'c', name_type_map['Uint64'], (0, None), (False, None), (None, None)
		yield 'events_list', name_type_map['Pointer'], (0, name_type_map['EventsList']), (False, None), (None, None)
		yield 'd', name_type_map['Uint64'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'abstract_name', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'concrete_name', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'prefab_name', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'a', name_type_map['Uint64'], (0, None), (False, None)
		yield 'b', name_type_map['Uint64'], (0, None), (False, None)
		yield 'c', name_type_map['Uint64'], (0, None), (False, None)
		yield 'events_list', name_type_map['Pointer'], (0, name_type_map['EventsList']), (False, None)
		yield 'd', name_type_map['Uint64'], (0, None), (False, None)

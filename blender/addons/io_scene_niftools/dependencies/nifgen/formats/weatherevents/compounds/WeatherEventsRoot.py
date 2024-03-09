from nifgen.formats.ovl_base.compounds.MemStruct import MemStruct
from nifgen.formats.weatherevents.imports import name_type_map


class WeatherEventsRoot(MemStruct):

	__name__ = 'WeatherEventsRoot'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.transition_time = name_type_map['Float'](self.context, 0, None)
		self.unknown_1 = name_type_map['Float'](self.context, 0, None)
		self.event_count = name_type_map['Uint64'](self.context, 0, None)
		self.unknown_2 = name_type_map['Uint64'](self.context, 0, None)
		self.resource_name = name_type_map['Pointer'](self.context, 0, name_type_map['ZStringObfuscated'])
		self.default_event_name = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		self.event_list = name_type_map['ArrayPointer'](self.context, self.event_count, name_type_map['WeatherEventData'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'resource_name', name_type_map['Pointer'], (0, name_type_map['ZStringObfuscated']), (False, None), (None, None)
		yield 'default_event_name', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'transition_time', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'unknown_1', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'event_list', name_type_map['ArrayPointer'], (None, name_type_map['WeatherEventData']), (False, None), (None, None)
		yield 'event_count', name_type_map['Uint64'], (0, None), (False, None), (None, None)
		yield 'unknown_2', name_type_map['Uint64'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'resource_name', name_type_map['Pointer'], (0, name_type_map['ZStringObfuscated']), (False, None)
		yield 'default_event_name', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'transition_time', name_type_map['Float'], (0, None), (False, None)
		yield 'unknown_1', name_type_map['Float'], (0, None), (False, None)
		yield 'event_list', name_type_map['ArrayPointer'], (instance.event_count, name_type_map['WeatherEventData']), (False, None)
		yield 'event_count', name_type_map['Uint64'], (0, None), (False, None)
		yield 'unknown_2', name_type_map['Uint64'], (0, None), (False, None)

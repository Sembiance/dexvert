from nifgen.formats.cinematic.imports import name_type_map
from nifgen.formats.ovl_base.compounds.MemStruct import MemStruct


class Event(MemStruct):

	"""
	32 bytes
	"""

	__name__ = 'Event'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.start_time = name_type_map['Float'](self.context, 0, None)
		self.b = name_type_map['Float'](self.context, 0, None)
		self.duration = name_type_map['Float'](self.context, 0, None)
		self.d = name_type_map['Float'](self.context, 0, None)
		self.module_name = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		self.attributes = name_type_map['Pointer'](self.context, 0, name_type_map['EventAttributes'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'start_time', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'b', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'module_name', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'attributes', name_type_map['Pointer'], (0, name_type_map['EventAttributes']), (False, None), (None, None)
		yield 'duration', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'd', name_type_map['Float'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'start_time', name_type_map['Float'], (0, None), (False, None)
		yield 'b', name_type_map['Float'], (0, None), (False, None)
		yield 'module_name', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'attributes', name_type_map['Pointer'], (0, name_type_map['EventAttributes']), (False, None)
		yield 'duration', name_type_map['Float'], (0, None), (False, None)
		yield 'd', name_type_map['Float'], (0, None), (False, None)

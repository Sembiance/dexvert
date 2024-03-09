from nifgen.formats.cinematic.imports import name_type_map
from nifgen.formats.ovl_base.compounds.MemStruct import MemStruct


class EventAttributes(MemStruct):

	"""
	24 bytes
	"""

	__name__ = 'EventAttributes'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.anim_name = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		self.event_name = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		self.empty_string = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'anim_name', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'event_name', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'empty_string', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'anim_name', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'event_name', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'empty_string', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)

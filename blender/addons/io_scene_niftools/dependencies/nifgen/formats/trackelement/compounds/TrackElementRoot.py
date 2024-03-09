from nifgen.formats.ovl_base.compounds.MemStruct import MemStruct
from nifgen.formats.trackelement.imports import name_type_map


class TrackElementRoot(MemStruct):

	"""
	PC: 32 bytes
	"""

	__name__ = 'TrackElementRoot'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.count = name_type_map['Uint64'](self.context, 0, None)
		self.track_data = name_type_map['ArrayPointer'](self.context, self.count, name_type_map['TrackElementData'])
		self.unk_string_1 = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		self.unk_string_2 = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'track_data', name_type_map['ArrayPointer'], (None, name_type_map['TrackElementData']), (False, None), (None, None)
		yield 'count', name_type_map['Uint64'], (0, None), (False, None), (None, None)
		yield 'unk_string_1', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'unk_string_2', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'track_data', name_type_map['ArrayPointer'], (instance.count, name_type_map['TrackElementData']), (False, None)
		yield 'count', name_type_map['Uint64'], (0, None), (False, None)
		yield 'unk_string_1', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'unk_string_2', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)

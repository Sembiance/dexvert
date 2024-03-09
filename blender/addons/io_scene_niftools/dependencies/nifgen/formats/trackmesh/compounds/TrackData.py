from nifgen.formats.ovl_base.compounds.MemStruct import MemStruct
from nifgen.formats.trackmesh.imports import name_type_map


class TrackData(MemStruct):

	"""
	PC: 48 bytes
	"""

	__name__ = 'TrackData'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.a = name_type_map['Uint'](self.context, 0, None)
		self.b = name_type_map['Uint'](self.context, 0, None)
		self.c = name_type_map['Uint64'](self.context, 0, None)
		self.d = name_type_map['Uint64'](self.context, 0, None)
		self.place_id = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		self.file = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		self.offset_id = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'place_id', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'file', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'a', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'b', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'c', name_type_map['Uint64'], (0, None), (False, None), (None, None)
		yield 'offset_id', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'd', name_type_map['Uint64'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'place_id', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'file', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'a', name_type_map['Uint'], (0, None), (False, None)
		yield 'b', name_type_map['Uint'], (0, None), (False, None)
		yield 'c', name_type_map['Uint64'], (0, None), (False, None)
		yield 'offset_id', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'd', name_type_map['Uint64'], (0, None), (False, None)

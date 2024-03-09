from nifgen.formats.ovl_base.compounds.MemStruct import MemStruct
from nifgen.formats.trackmesh.imports import name_type_map


class TrackMeshRoot(MemStruct):

	"""
	PC: 80 bytes
	"""

	__name__ = 'TrackMeshRoot'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.a = name_type_map['Uint64'](self.context, 0, None)
		self.count_0 = name_type_map['Uint'](self.context, 0, None)
		self.next_count = name_type_map['Uint'](self.context, 0, None)
		self.last_count = name_type_map['Uint64'](self.context, 0, None)
		self.lod_count = name_type_map['Uint64'](self.context, 0, None)
		self.g = name_type_map['Uint64'](self.context, 0, None)
		self.offset_data = name_type_map['ArrayPointer'](self.context, self.count_0, name_type_map['OffsetData'])
		self.track_data = name_type_map['ArrayPointer'](self.context, self.next_count, name_type_map['TrackData'])
		self.last = name_type_map['ArrayPointer'](self.context, self.last_count, name_type_map['LastData'])
		self.lods = name_type_map['ArrayPointer'](self.context, self.lod_count, name_type_map['Lod'])
		self.heatmap_name = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'a', name_type_map['Uint64'], (0, None), (False, None), (None, None)
		yield 'offset_data', name_type_map['ArrayPointer'], (None, name_type_map['OffsetData']), (False, None), (None, None)
		yield 'track_data', name_type_map['ArrayPointer'], (None, name_type_map['TrackData']), (False, None), (None, None)
		yield 'last', name_type_map['ArrayPointer'], (None, name_type_map['LastData']), (False, None), (None, None)
		yield 'count_0', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'next_count', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'last_count', name_type_map['Uint64'], (0, None), (False, None), (None, None)
		yield 'lods', name_type_map['ArrayPointer'], (None, name_type_map['Lod']), (False, None), (None, None)
		yield 'lod_count', name_type_map['Uint64'], (0, None), (False, None), (None, None)
		yield 'heatmap_name', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'g', name_type_map['Uint64'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'a', name_type_map['Uint64'], (0, None), (False, None)
		yield 'offset_data', name_type_map['ArrayPointer'], (instance.count_0, name_type_map['OffsetData']), (False, None)
		yield 'track_data', name_type_map['ArrayPointer'], (instance.next_count, name_type_map['TrackData']), (False, None)
		yield 'last', name_type_map['ArrayPointer'], (instance.last_count, name_type_map['LastData']), (False, None)
		yield 'count_0', name_type_map['Uint'], (0, None), (False, None)
		yield 'next_count', name_type_map['Uint'], (0, None), (False, None)
		yield 'last_count', name_type_map['Uint64'], (0, None), (False, None)
		yield 'lods', name_type_map['ArrayPointer'], (instance.lod_count, name_type_map['Lod']), (False, None)
		yield 'lod_count', name_type_map['Uint64'], (0, None), (False, None)
		yield 'heatmap_name', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'g', name_type_map['Uint64'], (0, None), (False, None)

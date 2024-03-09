from nifgen.array import Array
from nifgen.formats.ovl_base.compounds.MemStruct import MemStruct
from nifgen.formats.trackstation.imports import name_type_map


class TrackStationRoot(MemStruct):

	"""
	PC and PZ: 128 bytes
	"""

	__name__ = 'TrackStationRoot'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.unk_floats = Array(self.context, 0, None, (0,), name_type_map['Float'])
		self.unk_ints = Array(self.context, 0, None, (0,), name_type_map['Uint'])
		self.unk_ints_2 = Array(self.context, 0, None, (0,), name_type_map['Uint'])
		self.unk_floats_2 = Array(self.context, 0, None, (0,), name_type_map['Float'])
		self.unk_ints_3 = Array(self.context, 0, None, (0,), name_type_map['Uint'])
		self.some_dataa = name_type_map['Pointer'](self.context, 0, name_type_map['FirstPointersa'])
		self.some_datab = name_type_map['Pointer'](self.context, 0, name_type_map['FirstPointersb'])
		self.stationpiece_name_0 = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		self.stationpiece_name_1 = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		self.stationpiece_name_2 = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		self.stationpiece_name_3 = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		self.stationpiece_name_4 = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		self.stationpiece_name_5 = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		self.stationpiece_name_6 = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		self.stationpiece_name_7 = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'unk_floats', Array, (0, None, (2,), name_type_map['Float']), (False, None), (None, None)
		yield 'unk_ints', Array, (0, None, (2,), name_type_map['Uint']), (False, None), (None, None)
		yield 'some_dataa', name_type_map['Pointer'], (0, name_type_map['FirstPointersa']), (False, None), (None, None)
		yield 'some_datab', name_type_map['Pointer'], (0, name_type_map['FirstPointersb']), (False, None), (None, None)
		yield 'stationpiece_name_0', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'stationpiece_name_1', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'stationpiece_name_2', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'stationpiece_name_3', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'stationpiece_name_4', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'unk_ints_2', Array, (0, None, (2,), name_type_map['Uint']), (False, None), (None, None)
		yield 'stationpiece_name_5', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'stationpiece_name_6', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'stationpiece_name_7', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'unk_floats_2', Array, (0, None, (4,), name_type_map['Float']), (False, None), (None, None)
		yield 'unk_ints_3', Array, (0, None, (2,), name_type_map['Uint']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'unk_floats', Array, (0, None, (2,), name_type_map['Float']), (False, None)
		yield 'unk_ints', Array, (0, None, (2,), name_type_map['Uint']), (False, None)
		yield 'some_dataa', name_type_map['Pointer'], (0, name_type_map['FirstPointersa']), (False, None)
		yield 'some_datab', name_type_map['Pointer'], (0, name_type_map['FirstPointersb']), (False, None)
		yield 'stationpiece_name_0', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'stationpiece_name_1', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'stationpiece_name_2', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'stationpiece_name_3', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'stationpiece_name_4', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'unk_ints_2', Array, (0, None, (2,), name_type_map['Uint']), (False, None)
		yield 'stationpiece_name_5', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'stationpiece_name_6', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'stationpiece_name_7', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'unk_floats_2', Array, (0, None, (4,), name_type_map['Float']), (False, None)
		yield 'unk_ints_3', Array, (0, None, (2,), name_type_map['Uint']), (False, None)

from nifgen.array import Array
from nifgen.formats.ovl_base.compounds.MemStruct import MemStruct
from nifgen.formats.trackstation.imports import name_type_map


class CommonChunk(MemStruct):

	__name__ = 'CommonChunk'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.float_1 = name_type_map['Float'](self.context, 0, None)
		self.float_2 = name_type_map['Float'](self.context, 0, None)
		self.unk_flags_0 = Array(self.context, 0, None, (0,), name_type_map['Ubyte'])
		self.unk_flags_1 = Array(self.context, 0, None, (0,), name_type_map['Ubyte'])
		self.zero = name_type_map['Uint64'](self.context, 0, None)
		self.piece_name_0 = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		self.piece_name_1 = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		self.piece_name_2 = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		self.piece_name_3 = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		self.piece_name_4 = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		self.piece_name_5 = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		self.piece_name_6 = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		self.piece_name_7 = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		self.piece_name_8 = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'float_1', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'float_2', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'piece_name_0', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'piece_name_1', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'piece_name_2', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'unk_flags_0', Array, (0, None, (8,), name_type_map['Ubyte']), (False, None), (None, None)
		yield 'piece_name_3', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'piece_name_4', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'piece_name_5', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'unk_flags_1', Array, (0, None, (8,), name_type_map['Ubyte']), (False, None), (None, None)
		yield 'piece_name_6', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'piece_name_7', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'piece_name_8', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'zero', name_type_map['Uint64'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'float_1', name_type_map['Float'], (0, None), (False, None)
		yield 'float_2', name_type_map['Float'], (0, None), (False, None)
		yield 'piece_name_0', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'piece_name_1', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'piece_name_2', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'unk_flags_0', Array, (0, None, (8,), name_type_map['Ubyte']), (False, None)
		yield 'piece_name_3', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'piece_name_4', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'piece_name_5', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'unk_flags_1', Array, (0, None, (8,), name_type_map['Ubyte']), (False, None)
		yield 'piece_name_6', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'piece_name_7', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'piece_name_8', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'zero', name_type_map['Uint64'], (0, None), (False, None)

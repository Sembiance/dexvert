from nifgen.array import Array
from nifgen.base_struct import BaseStruct
from nifgen.formats.pdc.imports import name_type_map


class PDCWordList(BaseStruct):

	__name__ = 'PDCWordList'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.unknown_bytes_1 = Array(self.context, 0, None, (0,), name_type_map['Ubyte'])
		self.num_index_7 = name_type_map['Biguint32'](self.context, 0, None)
		self.index_7_array = Array(self.context, 0, None, (0,), name_type_map['Index7Bytes'])

		# Highest index value of structs in Index7Array
		self.max_index = name_type_map['Bigushort'](self.context, 0, None)

		# Guess it's a ushort, could also be 2 bytes.
		self.unknown_ushort_1 = name_type_map['Bigushort'](self.context, 0, None)

		# Bytes from start until "END" (so file size - 3)
		self.data_size = name_type_map['Biguint32'](self.context, 0, None)

		# 20 02 04 03, same in every file
		self.unknown_bytes_2 = Array(self.context, 0, None, (0,), name_type_map['Ubyte'])
		self.num_extra_ushorts = name_type_map['Bigushort'](self.context, 0, None)
		self.num_ushorts = name_type_map['Bigushort'](self.context, 0, None)
		self.ushorts = Array(self.context, 0, None, (0,), name_type_map['Bigushort'])
		self.extra_ushorts = Array(self.context, 0, None, (0,), name_type_map['Bigushort'])
		self.num_digraphs = name_type_map['Bigushort'](self.context, 0, None)

		# Seemingly always 6 less than Num Digraphs
		self.unknown_ushort_2 = name_type_map['Bigushort'](self.context, 0, None)

		# Again not really digraphs so much as some strings with yet-unspecified purpose.
		self.digraphs = Array(self.context, 0, name_type_map['Bigushort'], (0,), name_type_map['SizedString'])
		self.ushort_arrays = Array(self.context, 0, None, (0,), name_type_map['UshortArrayContainer'])
		self.extra_bytes = Array(self.context, 0, None, (0,), name_type_map['Ubyte'])

		# Last byte in example files always 1 less than num digraphs.
		self.unknown_bytes_3 = Array(self.context, 0, None, (0,), name_type_map['Ubyte'])
		self.num_int_arrays = name_type_map['Biguint32'](self.context, 0, None)
		self.int_arrays = Array(self.context, 0, None, (0,), name_type_map['Biguint32'])

		# Seemingly always 00, possibly unused.
		self.unknown_byte_1 = name_type_map['Ubyte'](self.context, 0, None)
		self.word_entries = Array(self.context, 0, None, (0,), name_type_map['WordEntry'])

		# Seemingly always 00, possibly unused.
		self.unknown_byte_2 = name_type_map['Ubyte'](self.context, 0, None)

		# "END"
		self.end = name_type_map['FixedString'](self.context, 3, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'unknown_bytes_1', Array, (0, None, (12,), name_type_map['Ubyte']), (False, None), (None, None)
		yield 'num_index_7', name_type_map['Biguint32'], (0, None), (False, None), (None, None)
		yield 'index_7_array', Array, (0, None, (None,), name_type_map['Index7Bytes']), (False, None), (None, None)
		yield 'max_index', name_type_map['Bigushort'], (0, None), (False, None), (None, None)
		yield 'unknown_ushort_1', name_type_map['Bigushort'], (0, None), (False, None), (None, None)
		yield 'data_size', name_type_map['Biguint32'], (0, None), (False, None), (None, None)
		yield 'unknown_bytes_2', Array, (0, None, (4,), name_type_map['Ubyte']), (False, None), (None, None)
		yield 'num_extra_ushorts', name_type_map['Bigushort'], (0, None), (False, None), (None, None)
		yield 'num_ushorts', name_type_map['Bigushort'], (0, None), (False, None), (None, None)
		yield 'ushorts', Array, (0, None, (None,), name_type_map['Bigushort']), (False, None), (None, None)
		yield 'extra_ushorts', Array, (0, None, (None,), name_type_map['Bigushort']), (False, None), (None, None)
		yield 'num_digraphs', name_type_map['Bigushort'], (0, None), (False, None), (None, None)
		yield 'unknown_ushort_2', name_type_map['Bigushort'], (0, None), (False, None), (None, None)
		yield 'digraphs', Array, (0, name_type_map['Bigushort'], (None,), name_type_map['SizedString']), (False, None), (None, None)
		yield 'ushort_arrays', Array, (0, None, (None,), name_type_map['UshortArrayContainer']), (False, None), (None, None)
		yield 'extra_bytes', Array, (0, None, (None,), name_type_map['Ubyte']), (False, None), (None, None)
		yield 'unknown_bytes_3', Array, (0, None, (3,), name_type_map['Ubyte']), (False, None), (None, None)
		yield 'num_int_arrays', name_type_map['Biguint32'], (0, None), (False, None), (None, None)
		yield 'int_arrays', Array, (0, None, (None, 4,), name_type_map['Biguint32']), (False, None), (None, None)
		yield 'unknown_byte_1', name_type_map['Ubyte'], (0, None), (False, None), (None, None)
		yield 'word_entries', Array, (0, None, (None,), name_type_map['WordEntry']), (False, None), (None, None)
		yield 'unknown_byte_2', name_type_map['Ubyte'], (0, None), (False, None), (None, None)
		yield 'end', name_type_map['FixedString'], (3, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'unknown_bytes_1', Array, (0, None, (12,), name_type_map['Ubyte']), (False, None)
		yield 'num_index_7', name_type_map['Biguint32'], (0, None), (False, None)
		yield 'index_7_array', Array, (0, None, (instance.num_index_7,), name_type_map['Index7Bytes']), (False, None)
		yield 'max_index', name_type_map['Bigushort'], (0, None), (False, None)
		yield 'unknown_ushort_1', name_type_map['Bigushort'], (0, None), (False, None)
		yield 'data_size', name_type_map['Biguint32'], (0, None), (False, None)
		yield 'unknown_bytes_2', Array, (0, None, (4,), name_type_map['Ubyte']), (False, None)
		yield 'num_extra_ushorts', name_type_map['Bigushort'], (0, None), (False, None)
		yield 'num_ushorts', name_type_map['Bigushort'], (0, None), (False, None)
		yield 'ushorts', Array, (0, None, (instance.num_ushorts,), name_type_map['Bigushort']), (False, None)
		yield 'extra_ushorts', Array, (0, None, (instance.num_extra_ushorts - instance.num_ushorts,), name_type_map['Bigushort']), (False, None)
		yield 'num_digraphs', name_type_map['Bigushort'], (0, None), (False, None)
		yield 'unknown_ushort_2', name_type_map['Bigushort'], (0, None), (False, None)
		yield 'digraphs', Array, (0, name_type_map['Bigushort'], (instance.num_digraphs,), name_type_map['SizedString']), (False, None)
		yield 'ushort_arrays', Array, (0, None, (instance.num_extra_ushorts - instance.num_digraphs,), name_type_map['UshortArrayContainer']), (False, None)
		yield 'extra_bytes', Array, (0, None, (instance.num_extra_ushorts,), name_type_map['Ubyte']), (False, None)
		yield 'unknown_bytes_3', Array, (0, None, (3,), name_type_map['Ubyte']), (False, None)
		yield 'num_int_arrays', name_type_map['Biguint32'], (0, None), (False, None)
		yield 'int_arrays', Array, (0, None, (instance.num_int_arrays, 4,), name_type_map['Biguint32']), (False, None)
		yield 'unknown_byte_1', name_type_map['Ubyte'], (0, None), (False, None)
		yield 'word_entries', Array, (0, None, (instance.arg,), name_type_map['WordEntry']), (False, None)
		yield 'unknown_byte_2', name_type_map['Ubyte'], (0, None), (False, None)
		yield 'end', name_type_map['FixedString'], (3, None), (False, None)

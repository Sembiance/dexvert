from nifgen.array import Array
from nifgen.base_struct import BaseStruct
from nifgen.formats.psi.imports import name_type_map


class Header(BaseStruct):

	__name__ = 'Header'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.copyright = name_type_map['SizedString'](self.context, 0, name_type_map['Bigushort'])
		self.unknown_bytes_1 = Array(self.context, 0, None, (0,), name_type_map['Ubyte'])
		self.num_phonemes = name_type_map['Bigushort'](self.context, 0, None)
		self.phonemes = Array(self.context, self.num_phonemes, None, (0,), name_type_map['PhonemeRecord'])
		self.num_similar_phonemes = name_type_map['Biguint32'](self.context, 0, None)
		self.similar_phonemes = Array(self.context, 0, None, (0,), name_type_map['SimilarPhonemeRecord'])
		self.num_unknown_structs = name_type_map['Bigushort'](self.context, 0, None)
		self.unknown_structs = Array(self.context, 0, None, (0,), name_type_map['UnknownStruct'])

		# 00 00 00 0A 00 00 13 88 00 XX, (last byte varies, rest is the same)
		self.unknown_bytes_2 = Array(self.context, 0, None, (0,), name_type_map['Ubyte'])

		# 00 00 00 0A 00 00 13 88 00 XX, (last byte is XX of Unknown Bytes 2 + 1)
		self.unknown_bytes_3 = Array(self.context, 0, None, (0,), name_type_map['Ubyte'])

		# 00 00 00 99 99 FF FF FF FF 00 00 00 03 00 00 00 83 00 00 00 C8 in every file
		self.unknown_bytes_4 = Array(self.context, 0, None, (0,), name_type_map['Ubyte'])

		# Seemingly always the same as Num Unknown Structs
		self.unknown_uint = name_type_map['Biguint32'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'copyright', name_type_map['SizedString'], (0, name_type_map['Bigushort']), (False, None), (None, None)
		yield 'unknown_bytes_1', Array, (0, None, (248,), name_type_map['Ubyte']), (False, None), (None, None)
		yield 'num_phonemes', name_type_map['Bigushort'], (0, None), (False, None), (None, None)
		yield 'phonemes', Array, (None, None, (None,), name_type_map['PhonemeRecord']), (False, None), (None, None)
		yield 'num_similar_phonemes', name_type_map['Biguint32'], (0, None), (False, None), (None, None)
		yield 'similar_phonemes', Array, (0, None, (None,), name_type_map['SimilarPhonemeRecord']), (False, None), (None, None)
		yield 'num_unknown_structs', name_type_map['Bigushort'], (0, None), (False, None), (None, None)
		yield 'unknown_structs', Array, (0, None, (None,), name_type_map['UnknownStruct']), (False, None), (None, None)
		yield 'unknown_bytes_2', Array, (0, None, (10,), name_type_map['Ubyte']), (False, None), (None, None)
		yield 'unknown_bytes_3', Array, (0, None, (10,), name_type_map['Ubyte']), (False, None), (None, None)
		yield 'unknown_bytes_4', Array, (0, None, (21,), name_type_map['Ubyte']), (False, None), (None, None)
		yield 'unknown_uint', name_type_map['Biguint32'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'copyright', name_type_map['SizedString'], (0, name_type_map['Bigushort']), (False, None)
		yield 'unknown_bytes_1', Array, (0, None, (248,), name_type_map['Ubyte']), (False, None)
		yield 'num_phonemes', name_type_map['Bigushort'], (0, None), (False, None)
		yield 'phonemes', Array, (instance.num_phonemes, None, (instance.num_phonemes,), name_type_map['PhonemeRecord']), (False, None)
		yield 'num_similar_phonemes', name_type_map['Biguint32'], (0, None), (False, None)
		yield 'similar_phonemes', Array, (0, None, (instance.num_similar_phonemes,), name_type_map['SimilarPhonemeRecord']), (False, None)
		yield 'num_unknown_structs', name_type_map['Bigushort'], (0, None), (False, None)
		yield 'unknown_structs', Array, (0, None, (instance.num_unknown_structs,), name_type_map['UnknownStruct']), (False, None)
		yield 'unknown_bytes_2', Array, (0, None, (10,), name_type_map['Ubyte']), (False, None)
		yield 'unknown_bytes_3', Array, (0, None, (10,), name_type_map['Ubyte']), (False, None)
		yield 'unknown_bytes_4', Array, (0, None, (21,), name_type_map['Ubyte']), (False, None)
		yield 'unknown_uint', name_type_map['Biguint32'], (0, None), (False, None)

from nifgen.array import Array
from nifgen.base_struct import BaseStruct
from nifgen.formats.pdc.imports import name_type_map


class G2Pb(BaseStruct):

	"""
	G2P likely stands for Grapheme to Phoneme
	"""

	__name__ = 'G2PB'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# "G2PB"
		self.magic = name_type_map['FixedString'](self.context, 4, None)

		# 20 02 09 05 00 00 00, same in every file
		self.unknown_1 = Array(self.context, 0, None, (0,), name_type_map['Ubyte'])

		# Byte that varies for files. Seemingly always 1 more than alphabet size.
		self.num_character_map_groups = name_type_map['Ubyte'](self.context, 0, None)
		self.unknown_2 = Array(self.context, 0, None, (0,), name_type_map['Ubyte'])
		self.alphabet_size = name_type_map['Ubyte'](self.context, 0, None)
		self.alphabet = Array(self.context, 0, None, (0,), name_type_map['Char'])

		# How many character maps per group
		self.character_map_groups = Array(self.context, 0, None, (0,), name_type_map['Biguint32'])
		self.num_words = name_type_map['Biguint32'](self.context, 0, None)
		self.unknown_ints_2 = Array(self.context, 0, None, (0,), name_type_map['Biguint32'])
		self.unknown_byte_2 = name_type_map['Ubyte'](self.context, 0, None)
		self.character_map = Array(self.context, 0, None, (0,), name_type_map['CharacterEntry'])
		self.small_words = Array(self.context, 0, name_type_map['Bigushort'], (0,), name_type_map['SizedString'])

		# Seemingly always 8 with the last one empty.
		self.alphabet_groups = Array(self.context, 0, name_type_map['Bigushort'], (0,), name_type_map['SizedString'])
		self.num_word_ends = name_type_map['Biguint32'](self.context, 0, None)
		self.word_ends = Array(self.context, 0, name_type_map['Bigushort'], (0,), name_type_map['SizedString'])
		self.num_digraphs = name_type_map['Biguint32'](self.context, 0, None)

		# Not really digraphs, contains some single letters, symbols and capital letters.
		self.digraphs = Array(self.context, 0, name_type_map['Bigushort'], (0,), name_type_map['SizedString'])

		# "ENDG2P"
		self.end = name_type_map['FixedString'](self.context, 6, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'magic', name_type_map['FixedString'], (4, None), (False, None), (None, None)
		yield 'unknown_1', Array, (0, None, (7,), name_type_map['Ubyte']), (False, None), (None, None)
		yield 'num_character_map_groups', name_type_map['Ubyte'], (0, None), (False, None), (None, None)
		yield 'unknown_2', Array, (0, None, (1,), name_type_map['Ubyte']), (False, None), (None, None)
		yield 'alphabet_size', name_type_map['Ubyte'], (0, None), (False, None), (None, None)
		yield 'alphabet', Array, (0, None, (None,), name_type_map['Char']), (False, None), (None, None)
		yield 'character_map_groups', Array, (0, None, (None,), name_type_map['Biguint32']), (False, None), (None, None)
		yield 'num_words', name_type_map['Biguint32'], (0, None), (False, None), (None, None)
		yield 'unknown_ints_2', Array, (0, None, (1,), name_type_map['Biguint32']), (False, None), (None, None)
		yield 'unknown_byte_2', name_type_map['Ubyte'], (0, None), (False, None), (None, None)
		yield 'character_map', Array, (0, None, (None, None,), name_type_map['CharacterEntry']), (False, None), (None, None)
		yield 'small_words', Array, (0, name_type_map['Bigushort'], (None,), name_type_map['SizedString']), (False, None), (None, None)
		yield 'alphabet_groups', Array, (0, name_type_map['Bigushort'], (7,), name_type_map['SizedString']), (False, None), (None, None)
		yield 'num_word_ends', name_type_map['Biguint32'], (0, None), (False, None), (None, None)
		yield 'word_ends', Array, (0, name_type_map['Bigushort'], (None,), name_type_map['SizedString']), (False, None), (None, None)
		yield 'num_digraphs', name_type_map['Biguint32'], (0, None), (False, None), (None, None)
		yield 'digraphs', Array, (0, name_type_map['Bigushort'], (None,), name_type_map['SizedString']), (False, None), (None, None)
		yield 'end', name_type_map['FixedString'], (6, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'magic', name_type_map['FixedString'], (4, None), (False, None)
		yield 'unknown_1', Array, (0, None, (7,), name_type_map['Ubyte']), (False, None)
		yield 'num_character_map_groups', name_type_map['Ubyte'], (0, None), (False, None)
		yield 'unknown_2', Array, (0, None, (1,), name_type_map['Ubyte']), (False, None)
		yield 'alphabet_size', name_type_map['Ubyte'], (0, None), (False, None)
		yield 'alphabet', Array, (0, None, (instance.alphabet_size,), name_type_map['Char']), (False, None)
		yield 'character_map_groups', Array, (0, None, (instance.num_character_map_groups,), name_type_map['Biguint32']), (False, None)
		yield 'num_words', name_type_map['Biguint32'], (0, None), (False, None)
		yield 'unknown_ints_2', Array, (0, None, (1,), name_type_map['Biguint32']), (False, None)
		yield 'unknown_byte_2', name_type_map['Ubyte'], (0, None), (False, None)
		yield 'character_map', Array, (0, None, (instance.num_character_map_groups, instance.character_map_groups,), name_type_map['CharacterEntry']), (False, None)
		yield 'small_words', Array, (0, name_type_map['Bigushort'], (instance.num_words,), name_type_map['SizedString']), (False, None)
		yield 'alphabet_groups', Array, (0, name_type_map['Bigushort'], (7,), name_type_map['SizedString']), (False, None)
		yield 'num_word_ends', name_type_map['Biguint32'], (0, None), (False, None)
		yield 'word_ends', Array, (0, name_type_map['Bigushort'], (instance.num_word_ends,), name_type_map['SizedString']), (False, None)
		yield 'num_digraphs', name_type_map['Biguint32'], (0, None), (False, None)
		yield 'digraphs', Array, (0, name_type_map['Bigushort'], (instance.num_digraphs,), name_type_map['SizedString']), (False, None)
		yield 'end', name_type_map['FixedString'], (6, None), (False, None)

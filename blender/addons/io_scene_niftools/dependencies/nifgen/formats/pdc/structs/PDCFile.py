from nifgen.array import Array
from nifgen.base_struct import BaseStruct
from nifgen.formats.pdc.imports import name_type_map


class PDCFile(BaseStruct):

	__name__ = 'PDCFile'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# DCC
		self.magic = name_type_map['LineString'](self.context, 0, None)

		# Version 112
		self.version = name_type_map['LineString'](self.context, 0, None)

		# Copyright notice
		self.copyright = name_type_map['LineString'](self.context, 0, None)

		# String describing number of words.
		self.num_words = name_type_map['LineString'](self.context, 0, None)

		# String saying "Rules Included"
		self.rules_included = name_type_map['LineString'](self.context, 0, None)

		# String saying "END_OF_HEADER"
		self.header_end = name_type_map['LineString'](self.context, 0, None)

		# 1A 01 in all files
		self.unknown_bytes_1 = Array(self.context, 0, None, (0,), name_type_map['Ubyte'])
		self.g_2_pb = name_type_map['G2Pb'](self.context, 0, None)

		# Number of words
		self.num_words = name_type_map['Biguint32'](self.context, 0, None)
		self.word_list = name_type_map['PDCWordList'](self.context, self.num_words, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'magic', name_type_map['LineString'], (0, None), (False, None), (None, None)
		yield 'version', name_type_map['LineString'], (0, None), (False, None), (None, None)
		yield 'copyright', name_type_map['LineString'], (0, None), (False, None), (None, None)
		yield 'num_words', name_type_map['LineString'], (0, None), (False, None), (None, None)
		yield 'rules_included', name_type_map['LineString'], (0, None), (False, None), (None, None)
		yield 'header_end', name_type_map['LineString'], (0, None), (False, None), (None, None)
		yield 'unknown_bytes_1', Array, (0, None, (2,), name_type_map['Ubyte']), (False, None), (None, None)
		yield 'g_2_pb', name_type_map['G2Pb'], (0, None), (False, None), (None, None)
		yield 'num_words', name_type_map['Biguint32'], (0, None), (False, None), (None, None)
		yield 'word_list', name_type_map['PDCWordList'], (None, None), (False, None), (None, True)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'magic', name_type_map['LineString'], (0, None), (False, None)
		yield 'version', name_type_map['LineString'], (0, None), (False, None)
		yield 'copyright', name_type_map['LineString'], (0, None), (False, None)
		yield 'num_words', name_type_map['LineString'], (0, None), (False, None)
		yield 'rules_included', name_type_map['LineString'], (0, None), (False, None)
		yield 'header_end', name_type_map['LineString'], (0, None), (False, None)
		yield 'unknown_bytes_1', Array, (0, None, (2,), name_type_map['Ubyte']), (False, None)
		yield 'g_2_pb', name_type_map['G2Pb'], (0, None), (False, None)
		yield 'num_words', name_type_map['Biguint32'], (0, None), (False, None)
		if instance.num_words != 0:
			yield 'word_list', name_type_map['PDCWordList'], (instance.num_words, None), (False, None)

from nifgen.array import Array
from nifgen.base_struct import BaseStruct
from nifgen.formats.psi.imports import name_type_map


class SimilarPhonemeRecord(BaseStruct):

	__name__ = 'SimilarPhonemeRecord'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# Seems to refer to similar phonemes in the Phonemes array (0-index)
		self.similar_index = name_type_map['Bigushort'](self.context, 0, None)
		self.num_phonemes = name_type_map['Bigushort'](self.context, 0, None)
		self.phonemes = Array(self.context, 0, name_type_map['Bigushort'], (0,), name_type_map['SizedString'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'similar_index', name_type_map['Bigushort'], (0, None), (False, None), (None, None)
		yield 'num_phonemes', name_type_map['Bigushort'], (0, None), (False, None), (None, None)
		yield 'phonemes', Array, (0, name_type_map['Bigushort'], (None,), name_type_map['SizedString']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'similar_index', name_type_map['Bigushort'], (0, None), (False, None)
		yield 'num_phonemes', name_type_map['Bigushort'], (0, None), (False, None)
		yield 'phonemes', Array, (0, name_type_map['Bigushort'], (instance.num_phonemes,), name_type_map['SizedString']), (False, None)

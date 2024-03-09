from nifgen.array import Array
from nifgen.base_struct import BaseStruct
from nifgen.formats.pdc.imports import name_type_map


class WordEntry(BaseStruct):

	"""
	Some kind of record presumably used to link words to their pronunciation.
	"""

	__name__ = 'WordEntry'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.num_bytes = name_type_map['Ubyte'](self.context, 0, None)

		# Word, followed by 00, followed by the rest of the data (which can have 00 in it).
		self.value = Array(self.context, 0, None, (0,), name_type_map['Ubyte'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'num_bytes', name_type_map['Ubyte'], (0, None), (False, None), (None, None)
		yield 'value', Array, (0, None, (None,), name_type_map['Ubyte']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'num_bytes', name_type_map['Ubyte'], (0, None), (False, None)
		yield 'value', Array, (0, None, (instance.num_bytes,), name_type_map['Ubyte']), (False, None)

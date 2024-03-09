from nifgen.array import Array
from nifgen.base_struct import BaseStruct
from nifgen.formats.ms2.imports import name_type_map


class StreamsZTHeader(BaseStruct):

	"""
	266 bytes ?
	very end of buffer 0 after the names list
	"""

	__name__ = 'StreamsZTHeader'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# sometimes 00 byte
		self.weird_padding = name_type_map['SmartPadding'](self.context, 0, None)

		# ?
		self.unks = Array(self.context, 0, None, (0,), name_type_map['InfoZTMemPool'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'weird_padding', name_type_map['SmartPadding'], (0, None), (False, None), (None, None)
		yield 'unks', Array, (0, None, (None,), name_type_map['InfoZTMemPool']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'weird_padding', name_type_map['SmartPadding'], (0, None), (False, None)
		yield 'unks', Array, (0, None, (instance.arg.static_buffer_index,), name_type_map['InfoZTMemPool']), (False, None)

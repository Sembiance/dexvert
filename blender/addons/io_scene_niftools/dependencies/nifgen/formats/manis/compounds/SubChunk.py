from nifgen.array import Array
from nifgen.base_struct import BaseStruct
from nifgen.formats.manis.imports import name_type_map


class SubChunk(BaseStruct):

	"""
	arg is chunksizes
	"""

	__name__ = 'SubChunk'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# for subchunk_list[n] needs chunksize_list[n]'s counta for array length
		self.weird_list_one = Array(self.context, 0, None, (0,), name_type_map['WeirdElementOne'])

		# needs sum of countb's from weird list one
		self.weird_list_two = name_type_map['WeirdElementTwoReader'](self.context, self.weird_list_one, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'weird_list_one', Array, (0, None, (None,), name_type_map['WeirdElementOne']), (False, None), (None, None)
		yield 'weird_list_two', name_type_map['WeirdElementTwoReader'], (None, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'weird_list_one', Array, (0, None, (instance.arg.counta,), name_type_map['WeirdElementOne']), (False, None)
		yield 'weird_list_two', name_type_map['WeirdElementTwoReader'], (instance.weird_list_one, None), (False, None)

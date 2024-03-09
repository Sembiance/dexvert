from nifgen.base_struct import BaseStruct
from nifgen.formats.ms2.imports import name_type_map


class ZerosPadding(BaseStruct):

	"""
	1 bit per bone, padded to 8 bytes, all 00
	"""

	__name__ = 'ZerosPadding'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.hier_2_padding_0 = name_type_map['Uint64'](self.context, 0, None)

		# 128 still has 16 bytes
		self.hier_2_padding_1 = name_type_map['Uint64'](self.context, 0, None)

		# 129 is the first with 24 bytes
		self.hier_2_padding_2 = name_type_map['Uint64'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'hier_2_padding_0', name_type_map['Uint64'], (0, None), (False, None), (None, None)
		yield 'hier_2_padding_1', name_type_map['Uint64'], (0, None), (False, None), (None, True)
		yield 'hier_2_padding_2', name_type_map['Uint64'], (0, None), (False, None), (None, True)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'hier_2_padding_0', name_type_map['Uint64'], (0, None), (False, None)
		if 64 < instance.arg:
			yield 'hier_2_padding_1', name_type_map['Uint64'], (0, None), (False, None)
		if 128 < instance.arg:
			yield 'hier_2_padding_2', name_type_map['Uint64'], (0, None), (False, None)

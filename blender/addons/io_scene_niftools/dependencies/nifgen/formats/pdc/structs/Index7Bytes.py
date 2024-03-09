from nifgen.array import Array
from nifgen.base_struct import BaseStruct
from nifgen.formats.pdc.imports import name_type_map


class Index7Bytes(BaseStruct):

	"""
	A 7-byte struct, appearing to have an index spanning the 4th and 5th byte.
	"""

	__name__ = 'Index7Bytes'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# 3 bytes of which the meaning is not certain
		self.unknown_bytes_1 = Array(self.context, 0, None, (0,), name_type_map['Ubyte'])

		# Presumably some kind of index into groupings.
		self.index = name_type_map['Bigushort'](self.context, 0, None)

		# 1 bytes of which the meaning is not certain
		self.unknown_bytes_2 = Array(self.context, 0, None, (0,), name_type_map['Ubyte'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'unknown_bytes_1', Array, (0, None, (3,), name_type_map['Ubyte']), (False, None), (None, None)
		yield 'index', name_type_map['Bigushort'], (0, None), (False, None), (None, None)
		yield 'unknown_bytes_2', Array, (0, None, (2,), name_type_map['Ubyte']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'unknown_bytes_1', Array, (0, None, (3,), name_type_map['Ubyte']), (False, None)
		yield 'index', name_type_map['Bigushort'], (0, None), (False, None)
		yield 'unknown_bytes_2', Array, (0, None, (2,), name_type_map['Ubyte']), (False, None)

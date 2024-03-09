from nifgen.array import Array
from nifgen.base_struct import BaseStruct
from nifgen.formats.ms2.imports import name_type_map


class ZtVertBlockInfo(BaseStruct):

	"""
	16 bytes total
	"""

	__name__ = 'ZtVertBlockInfo'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.vertex_count = name_type_map['Uint'](self.context, 0, None)
		self.flags = Array(self.context, 0, None, (0,), name_type_map['Ubyte'])
		self.zero = name_type_map['Uint'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'vertex_count', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'flags', Array, (0, None, (8,), name_type_map['Ubyte']), (False, None), (None, None)
		yield 'zero', name_type_map['Uint'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'vertex_count', name_type_map['Uint'], (0, None), (False, None)
		yield 'flags', Array, (0, None, (8,), name_type_map['Ubyte']), (False, None)
		yield 'zero', name_type_map['Uint'], (0, None), (False, None)

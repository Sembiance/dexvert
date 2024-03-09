from nifgen.base_struct import BaseStruct
from nifgen.formats.ms2.imports import name_type_map


class ZtTriBlockInfo(BaseStruct):

	"""
	8 bytes total
	"""

	__name__ = 'ZtTriBlockInfo'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.tri_index_count = name_type_map['Uint'](self.context, 0, None)
		self.a = name_type_map['Short'](self.context, 0, None)
		self.unk_index = name_type_map['Short'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'tri_index_count', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'a', name_type_map['Short'], (0, None), (False, None), (None, None)
		yield 'unk_index', name_type_map['Short'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'tri_index_count', name_type_map['Uint'], (0, None), (False, None)
		yield 'a', name_type_map['Short'], (0, None), (False, None)
		yield 'unk_index', name_type_map['Short'], (0, None), (False, None)

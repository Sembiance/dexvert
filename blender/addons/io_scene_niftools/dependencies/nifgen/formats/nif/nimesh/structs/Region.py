from nifgen.base_struct import BaseStruct
from nifgen.formats.nif.imports import name_type_map


class Region(BaseStruct):

	"""
	A range of indices, which make up a region (such as a submesh).
	"""

	__name__ = 'Region'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.start_index = name_type_map['Uint'](self.context, 0, None)
		self.num_indices = name_type_map['Uint'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'start_index', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'num_indices', name_type_map['Uint'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'start_index', name_type_map['Uint'], (0, None), (False, None)
		yield 'num_indices', name_type_map['Uint'], (0, None), (False, None)

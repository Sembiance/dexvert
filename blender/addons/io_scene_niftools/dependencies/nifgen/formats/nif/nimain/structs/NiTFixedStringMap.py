from nifgen.array import Array
from nifgen.base_struct import BaseStruct
from nifgen.formats.nif.imports import name_type_map


class NiTFixedStringMap(BaseStruct):

	"""
	A mapping or hash table between NiFixedString keys and a generic value.
	Currently, #T# must be a basic type due to nif.xml restrictions.
	"""

	__name__ = 'NiTFixedStringMap'


	def __init__(self, context, arg=0, template=None, set_default=True):
		if template is None:
			raise TypeError(f'{type(self).__name__} requires template is not None')
		super().__init__(context, arg, template, set_default=False)
		self.num_strings = name_type_map['Uint'](self.context, 0, None)
		self.strings = Array(self.context, 0, self.template, (0,), name_type_map['NiTFixedStringMapItem'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'num_strings', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'strings', Array, (0, None, (None,), name_type_map['NiTFixedStringMapItem']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'num_strings', name_type_map['Uint'], (0, None), (False, None)
		yield 'strings', Array, (0, instance.template, (instance.num_strings,), name_type_map['NiTFixedStringMapItem']), (False, None)

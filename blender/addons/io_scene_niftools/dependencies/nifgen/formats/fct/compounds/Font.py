from nifgen.formats.fct.imports import name_type_map
from nifgen.formats.ovl_base.compounds.MemStruct import MemStruct


class Font(MemStruct):

	"""
	JWE: 16 bytes
	"""

	__name__ = 'Font'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.data_size = name_type_map['Uint64'](self.context, 0, None)
		self.zero = name_type_map['Uint64'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'data_size', name_type_map['Uint64'], (0, None), (False, None), (None, None)
		yield 'zero', name_type_map['Uint64'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'data_size', name_type_map['Uint64'], (0, None), (False, None)
		yield 'zero', name_type_map['Uint64'], (0, None), (False, None)

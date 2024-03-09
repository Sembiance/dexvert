from nifgen.formats.fgm.compounds.GenericInfo import GenericInfo
from nifgen.formats.fgm.imports import name_type_map


class AttribInfo(GenericInfo):

	"""
	part of fgm fragment, repeated per attribute
	"""

	__name__ = 'AttribInfo'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# byte offset to first value in the data_lib pointer, usually or always sorted in stock
		self._value_offset = name_type_map['Uint64'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield '_value_offset', name_type_map['Uint64'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield '_value_offset', name_type_map['Uint64'], (0, None), (False, None)

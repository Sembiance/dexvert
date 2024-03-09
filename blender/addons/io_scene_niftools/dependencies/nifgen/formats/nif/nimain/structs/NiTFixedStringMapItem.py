from nifgen.base_struct import BaseStruct
from nifgen.formats.nif.imports import name_type_map


class NiTFixedStringMapItem(BaseStruct):

	"""
	Currently, #T# must be a basic type due to nif.xml restrictions.
	"""

	__name__ = 'NiTFixedStringMapItem'


	def __init__(self, context, arg=0, template=None, set_default=True):
		if template is None:
			raise TypeError(f'{type(self).__name__} requires template is not None')
		super().__init__(context, arg, template, set_default=False)
		self.string = name_type_map['NiFixedString'](self.context, 0, None)
		self.value = self.template(self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'string', name_type_map['NiFixedString'], (0, None), (False, None), (None, None)
		yield 'value', None, (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'string', name_type_map['NiFixedString'], (0, None), (False, None)
		yield 'value', instance.template, (0, None), (False, None)

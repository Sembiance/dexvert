from nifgen.array import Array
from nifgen.base_struct import BaseStruct
from nifgen.formats.pdc.imports import name_type_map


class CharacterEntry(BaseStruct):

	__name__ = 'CharacterEntry'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.values = Array(self.context, 0, name_type_map['Bigushort'], (0,), name_type_map['SizedString'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'values', Array, (0, name_type_map['Bigushort'], (4,), name_type_map['SizedString']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'values', Array, (0, name_type_map['Bigushort'], (4,), name_type_map['SizedString']), (False, None)

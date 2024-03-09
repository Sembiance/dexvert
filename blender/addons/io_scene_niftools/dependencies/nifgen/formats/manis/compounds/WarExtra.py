from nifgen.array import Array
from nifgen.base_struct import BaseStruct
from nifgen.formats.manis.imports import name_type_map


class WarExtra(BaseStruct):

	__name__ = 'WarExtra'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.zeros = Array(self.context, 0, None, (0,), name_type_map['Uint'])
		self.stuff = Array(self.context, 0, None, (0,), name_type_map['WarExtraPart'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'zeros', Array, (0, None, (1,), name_type_map['Uint']), (False, None), (None, None)
		yield 'stuff', Array, (0, None, (4,), name_type_map['WarExtraPart']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'zeros', Array, (0, None, (1,), name_type_map['Uint']), (False, None)
		yield 'stuff', Array, (0, None, (4,), name_type_map['WarExtraPart']), (False, None)

from nifgen.array import Array
from nifgen.base_struct import BaseStruct
from nifgen.formats.manis.imports import name_type_map


class WarExtraPart(BaseStruct):

	__name__ = 'WarExtraPart'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.stuff = Array(self.context, 0, None, (0,), name_type_map['Ushort'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'stuff', Array, (0, None, (24,), name_type_map['Ushort']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'stuff', Array, (0, None, (24,), name_type_map['Ushort']), (False, None)

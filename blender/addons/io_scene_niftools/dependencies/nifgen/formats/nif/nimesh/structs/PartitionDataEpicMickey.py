from nifgen.array import Array
from nifgen.base_struct import BaseStruct
from nifgen.formats.nif.imports import name_type_map


class PartitionDataEpicMickey(BaseStruct):

	__name__ = 'PartitionDataEpicMickey'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.start = name_type_map['Int'](self.context, 0, None)
		self.end = name_type_map['Int'](self.context, 0, None)
		self.weight_indices = Array(self.context, 0, None, (0,), name_type_map['Ushort'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'start', name_type_map['Int'], (0, None), (False, None), (None, None)
		yield 'end', name_type_map['Int'], (0, None), (False, None), (None, None)
		yield 'weight_indices', Array, (0, None, (10,), name_type_map['Ushort']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'start', name_type_map['Int'], (0, None), (False, None)
		yield 'end', name_type_map['Int'], (0, None), (False, None)
		yield 'weight_indices', Array, (0, None, (10,), name_type_map['Ushort']), (False, None)

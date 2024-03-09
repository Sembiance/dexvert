from nifgen.array import Array
from nifgen.base_struct import BaseStruct
from nifgen.formats.nif.imports import name_type_map


class WeightDataEpicMickey(BaseStruct):

	__name__ = 'WeightDataEpicMickey'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.bone_indices = Array(self.context, 0, None, (0,), name_type_map['Int'])
		self.weights = Array(self.context, 0, None, (0,), name_type_map['Float'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'bone_indices', Array, (0, None, (3,), name_type_map['Int']), (False, None), (None, None)
		yield 'weights', Array, (0, None, (3,), name_type_map['Float']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'bone_indices', Array, (0, None, (3,), name_type_map['Int']), (False, None)
		yield 'weights', Array, (0, None, (3,), name_type_map['Float']), (False, None)

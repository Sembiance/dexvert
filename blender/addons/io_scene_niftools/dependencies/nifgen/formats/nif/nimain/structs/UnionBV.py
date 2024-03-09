from nifgen.array import Array
from nifgen.base_struct import BaseStruct
from nifgen.formats.nif.imports import name_type_map


class UnionBV(BaseStruct):

	__name__ = 'UnionBV'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.num_bv = name_type_map['Uint'](self.context, 0, None)
		self.bounding_volumes = Array(self.context, 0, None, (0,), name_type_map['BoundingVolume'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'num_bv', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'bounding_volumes', Array, (0, None, (None,), name_type_map['BoundingVolume']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'num_bv', name_type_map['Uint'], (0, None), (False, None)
		yield 'bounding_volumes', Array, (0, None, (instance.num_bv,), name_type_map['BoundingVolume']), (False, None)

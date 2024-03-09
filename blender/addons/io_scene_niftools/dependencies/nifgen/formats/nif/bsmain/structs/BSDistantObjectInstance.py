from nifgen.array import Array
from nifgen.base_struct import BaseStruct
from nifgen.formats.nif.imports import name_type_map


class BSDistantObjectInstance(BaseStruct):

	__name__ = 'BSDistantObjectInstance'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.resource_id = name_type_map['BSResourceID'](self.context, 0, None)
		self.num_unknown_data = name_type_map['Uint'](self.context, 0, None)
		self.unknown_data = Array(self.context, 0, None, (0,), name_type_map['BSDistantObjectUnknown'])
		self.num_transforms = name_type_map['Uint'](self.context, 0, None)
		self.transforms = Array(self.context, 0, None, (0,), name_type_map['Matrix44'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'resource_id', name_type_map['BSResourceID'], (0, None), (False, None), (None, None)
		yield 'num_unknown_data', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'unknown_data', Array, (0, None, (None,), name_type_map['BSDistantObjectUnknown']), (False, None), (None, None)
		yield 'num_transforms', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'transforms', Array, (0, None, (None,), name_type_map['Matrix44']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'resource_id', name_type_map['BSResourceID'], (0, None), (False, None)
		yield 'num_unknown_data', name_type_map['Uint'], (0, None), (False, None)
		yield 'unknown_data', Array, (0, None, (instance.num_unknown_data,), name_type_map['BSDistantObjectUnknown']), (False, None)
		yield 'num_transforms', name_type_map['Uint'], (0, None), (False, None)
		yield 'transforms', Array, (0, None, (instance.num_transforms,), name_type_map['Matrix44']), (False, None)

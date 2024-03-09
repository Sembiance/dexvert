from nifgen.base_struct import BaseStruct
from nifgen.formats.nif.imports import name_type_map


class BhkWorldObjCInfoProperty(BaseStruct):

	"""
	hkWorldObjectCinfo::Property struct
	"""

	__name__ = 'bhkWorldObjCInfoProperty'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.data = name_type_map['Uint'].from_value(0)
		self.size = name_type_map['Uint'].from_value(0)
		self.capacity_and_flags = name_type_map['Uint'].from_value(2147483648)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'data', name_type_map['Uint'], (0, None), (False, 0), (None, None)
		yield 'size', name_type_map['Uint'], (0, None), (False, 0), (None, None)
		yield 'capacity_and_flags', name_type_map['Uint'], (0, None), (False, 2147483648), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'data', name_type_map['Uint'], (0, None), (False, 0)
		yield 'size', name_type_map['Uint'], (0, None), (False, 0)
		yield 'capacity_and_flags', name_type_map['Uint'], (0, None), (False, 2147483648)

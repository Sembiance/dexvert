from nifgen.base_struct import BaseStruct
from nifgen.formats.manis.imports import name_type_map


class LocBound(BaseStruct):

	__name__ = 'LocBound'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.loc_min = name_type_map['Vector3'](self.context, 0, None)
		self.loc_extent = name_type_map['Vector3'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'loc_min', name_type_map['Vector3'], (0, None), (False, None), (None, None)
		yield 'loc_extent', name_type_map['Vector3'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'loc_min', name_type_map['Vector3'], (0, None), (False, None)
		yield 'loc_extent', name_type_map['Vector3'], (0, None), (False, None)

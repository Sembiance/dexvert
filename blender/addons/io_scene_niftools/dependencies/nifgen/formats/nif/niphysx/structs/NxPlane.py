from nifgen.base_struct import BaseStruct
from nifgen.formats.nif.imports import name_type_map


class NxPlane(BaseStruct):

	__name__ = 'NxPlane'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.val_1 = name_type_map['Float'](self.context, 0, None)
		self.point_1 = name_type_map['Vector3'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'val_1', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'point_1', name_type_map['Vector3'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'val_1', name_type_map['Float'], (0, None), (False, None)
		yield 'point_1', name_type_map['Vector3'], (0, None), (False, None)

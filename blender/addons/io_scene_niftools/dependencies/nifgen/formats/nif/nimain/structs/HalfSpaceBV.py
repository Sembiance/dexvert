from nifgen.base_struct import BaseStruct
from nifgen.formats.nif.imports import name_type_map


class HalfSpaceBV(BaseStruct):

	__name__ = 'HalfSpaceBV'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.plane = name_type_map['NiPlane'](self.context, 0, None)
		self.center = name_type_map['Vector3'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'plane', name_type_map['NiPlane'], (0, None), (False, None), (None, None)
		yield 'center', name_type_map['Vector3'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'plane', name_type_map['NiPlane'], (0, None), (False, None)
		yield 'center', name_type_map['Vector3'], (0, None), (False, None)

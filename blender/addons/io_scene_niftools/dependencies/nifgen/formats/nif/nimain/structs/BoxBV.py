from nifgen.array import Array
from nifgen.base_struct import BaseStruct
from nifgen.formats.nif.imports import name_type_map


class BoxBV(BaseStruct):

	"""
	Box Bounding Volume
	"""

	__name__ = 'BoxBV'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.center = name_type_map['Vector3'](self.context, 0, None)
		self.axis = Array(self.context, 0, None, (0,), name_type_map['Vector3'])
		self.extent = name_type_map['Vector3'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'center', name_type_map['Vector3'], (0, None), (False, None), (None, None)
		yield 'axis', Array, (0, None, (3,), name_type_map['Vector3']), (False, None), (None, None)
		yield 'extent', name_type_map['Vector3'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'center', name_type_map['Vector3'], (0, None), (False, None)
		yield 'axis', Array, (0, None, (3,), name_type_map['Vector3']), (False, None)
		yield 'extent', name_type_map['Vector3'], (0, None), (False, None)

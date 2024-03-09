from nifgen.array import Array
from nifgen.base_struct import BaseStruct
from nifgen.formats.ms2.imports import name_type_map


class BoundingBox(BaseStruct):

	__name__ = 'BoundingBox'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.rotation = name_type_map['Matrix33'](self.context, 0, None)

		# center of the box
		self.center = name_type_map['Vector3'](self.context, 0, None)

		# total width
		self.extent = name_type_map['Vector3'](self.context, 0, None)

		# probably padding
		self.zeros = Array(self.context, 0, None, (0,), name_type_map['Uint'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'rotation', name_type_map['Matrix33'], (0, None), (False, None), (None, None)
		yield 'center', name_type_map['Vector3'], (0, None), (False, None), (None, None)
		yield 'extent', name_type_map['Vector3'], (0, None), (False, None), (None, None)
		yield 'zeros', Array, (0, None, (3,), name_type_map['Uint']), (False, None), (lambda context: context.version == 32, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'rotation', name_type_map['Matrix33'], (0, None), (False, None)
		yield 'center', name_type_map['Vector3'], (0, None), (False, None)
		yield 'extent', name_type_map['Vector3'], (0, None), (False, None)
		if instance.context.version == 32:
			yield 'zeros', Array, (0, None, (3,), name_type_map['Uint']), (False, None)

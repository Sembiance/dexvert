from nifgen.base_struct import BaseStruct
from nifgen.formats.voxelskirt.imports import name_type_map


class Area(BaseStruct):

	"""
	40 bytes
	"""

	__name__ = 'Area'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# index into name list
		self._id = name_type_map['Uint64'](self.context, 0, None)
		self.width_1 = name_type_map['Uint64'](self.context, 0, None)
		self.height_1 = name_type_map['Uint64'](self.context, 0, None)
		self.width_2 = name_type_map['Uint64'](self.context, 0, None)
		self.height_2 = name_type_map['Uint64'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield '_id', name_type_map['Uint64'], (0, None), (False, None), (None, None)
		yield 'width_1', name_type_map['Uint64'], (0, None), (False, None), (None, None)
		yield 'height_1', name_type_map['Uint64'], (0, None), (False, None), (None, None)
		yield 'width_2', name_type_map['Uint64'], (0, None), (False, None), (None, None)
		yield 'height_2', name_type_map['Uint64'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield '_id', name_type_map['Uint64'], (0, None), (False, None)
		yield 'width_1', name_type_map['Uint64'], (0, None), (False, None)
		yield 'height_1', name_type_map['Uint64'], (0, None), (False, None)
		yield 'width_2', name_type_map['Uint64'], (0, None), (False, None)
		yield 'height_2', name_type_map['Uint64'], (0, None), (False, None)

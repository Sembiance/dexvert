from nifgen.base_struct import BaseStruct
from nifgen.formats.voxelskirt.imports import name_type_map


class Layer(BaseStruct):

	"""
	32 bytes
	PZ and JWE only, describes a data layer image
	"""

	__name__ = 'Layer'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# index into name list
		self._id = name_type_map['Uint64'](self.context, 0, None)
		self.dtype = name_type_map['VxlDtype'](self.context, 0, None)

		# address of this data layer
		self._offset = name_type_map['Uint64'](self.context, 0, None)

		# data size of this layer, in bytes
		self._data_size = name_type_map['Uint64'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield '_id', name_type_map['Uint64'], (0, None), (False, None), (None, None)
		yield 'dtype', name_type_map['VxlDtype'], (0, None), (False, None), (None, None)
		yield '_offset', name_type_map['Uint64'], (0, None), (False, None), (None, None)
		yield '_data_size', name_type_map['Uint64'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield '_id', name_type_map['Uint64'], (0, None), (False, None)
		yield 'dtype', name_type_map['VxlDtype'], (0, None), (False, None)
		yield '_offset', name_type_map['Uint64'], (0, None), (False, None)
		yield '_data_size', name_type_map['Uint64'], (0, None), (False, None)

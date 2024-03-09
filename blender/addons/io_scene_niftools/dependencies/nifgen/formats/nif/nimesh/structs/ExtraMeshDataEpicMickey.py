from nifgen.array import Array
from nifgen.base_struct import BaseStruct
from nifgen.formats.nif.imports import name_type_map


class ExtraMeshDataEpicMickey(BaseStruct):

	__name__ = 'ExtraMeshDataEpicMickey'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# 1 if it has weights, 0 otherwise.
		self.has_weights = name_type_map['Uint'](self.context, 0, None)

		# Total number of floats in the bone transform matrices - divide by 16 to get the number of matrices.
		self.num_transform_floats = name_type_map['Uint'](self.context, 0, None)

		# Transform matrices corresponding to the bones. Note: Stored transposed to normally.
		self.bone_transforms = Array(self.context, 0, None, (0,), name_type_map['Matrix44'])
		self.num_weights = name_type_map['Uint'](self.context, 0, None)
		self.weights = Array(self.context, 0, None, (0,), name_type_map['WeightDataEpicMickey'])
		self.vertex_to_weight_map_size = name_type_map['Uint'](self.context, 0, None)
		self.vertex_to_weight_map = Array(self.context, 0, None, (0,), name_type_map['Uint'])
		self.unknown_data_size = name_type_map['Uint'](self.context, 0, None)
		self.unknown_data_width = name_type_map['Uint'](self.context, 0, None)
		self.unknown_data = Array(self.context, 0, None, (0,), name_type_map['Vector3'])
		self.unknown_indices = Array(self.context, 0, None, (0,), name_type_map['Ushort'])

		# When non-zero, equal to the number of primitives.
		self.num_mapped_primitives = name_type_map['Uint'](self.context, 0, None)

		# Some integer associated with each primitive.
		self.mapped_primitives = Array(self.context, 0, None, (0,), name_type_map['Byte'])
		self.partition_size = name_type_map['Uint'](self.context, 0, None)
		self.partitions = Array(self.context, 0, None, (0,), name_type_map['PartitionDataEpicMickey'])

		# The max value to appear in the Mapped Primitives array.
		self.max_primitive_map_index = name_type_map['Uint'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'has_weights', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'num_transform_floats', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'bone_transforms', Array, (0, None, (None,), name_type_map['Matrix44']), (False, None), (None, None)
		yield 'num_weights', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'weights', Array, (0, None, (None,), name_type_map['WeightDataEpicMickey']), (False, None), (None, None)
		yield 'vertex_to_weight_map_size', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'vertex_to_weight_map', Array, (0, None, (None,), name_type_map['Uint']), (False, None), (None, None)
		yield 'unknown_data_size', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'unknown_data_width', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'unknown_data', Array, (0, None, (None, None,), name_type_map['Vector3']), (False, None), (None, None)
		yield 'unknown_indices', Array, (0, None, (None,), name_type_map['Ushort']), (False, None), (None, None)
		yield 'num_mapped_primitives', name_type_map['Ushort'], (0, None), (False, None), (lambda context: context.user_version < 17, None)
		yield 'num_mapped_primitives', name_type_map['Uint'], (0, None), (False, None), (lambda context: context.user_version == 17, None)
		yield 'mapped_primitives', Array, (0, None, (None,), name_type_map['Byte']), (False, None), (None, None)
		yield 'partition_size', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'partitions', Array, (0, None, (None,), name_type_map['PartitionDataEpicMickey']), (False, None), (None, None)
		yield 'max_primitive_map_index', name_type_map['Uint'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'has_weights', name_type_map['Uint'], (0, None), (False, None)
		yield 'num_transform_floats', name_type_map['Uint'], (0, None), (False, None)
		yield 'bone_transforms', Array, (0, None, (int(instance.num_transform_floats / 16),), name_type_map['Matrix44']), (False, None)
		yield 'num_weights', name_type_map['Uint'], (0, None), (False, None)
		yield 'weights', Array, (0, None, (instance.num_weights,), name_type_map['WeightDataEpicMickey']), (False, None)
		yield 'vertex_to_weight_map_size', name_type_map['Uint'], (0, None), (False, None)
		yield 'vertex_to_weight_map', Array, (0, None, (instance.vertex_to_weight_map_size,), name_type_map['Uint']), (False, None)
		yield 'unknown_data_size', name_type_map['Uint'], (0, None), (False, None)
		yield 'unknown_data_width', name_type_map['Uint'], (0, None), (False, None)
		yield 'unknown_data', Array, (0, None, (instance.unknown_data_size, instance.unknown_data_width,), name_type_map['Vector3']), (False, None)
		yield 'unknown_indices', Array, (0, None, (instance.unknown_data_size,), name_type_map['Ushort']), (False, None)
		if instance.context.user_version < 17:
			yield 'num_mapped_primitives', name_type_map['Ushort'], (0, None), (False, None)
		if instance.context.user_version == 17:
			yield 'num_mapped_primitives', name_type_map['Uint'], (0, None), (False, None)
		yield 'mapped_primitives', Array, (0, None, (instance.num_mapped_primitives,), name_type_map['Byte']), (False, None)
		yield 'partition_size', name_type_map['Uint'], (0, None), (False, None)
		yield 'partitions', Array, (0, None, (instance.partition_size,), name_type_map['PartitionDataEpicMickey']), (False, None)
		yield 'max_primitive_map_index', name_type_map['Uint'], (0, None), (False, None)

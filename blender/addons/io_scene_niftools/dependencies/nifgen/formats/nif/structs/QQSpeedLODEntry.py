from nifgen.array import Array
from nifgen.base_struct import BaseStruct
from nifgen.formats.nif.imports import name_type_map


class QQSpeedLODEntry(BaseStruct):

	__name__ = 'QQSpeedLODEntry'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# Seemingly always zeros.
		self.unknown_bytes = Array(self.context, 0, None, (0,), name_type_map['Byte'])

		# Always 3 in tested mesh.
		self.num_levels = name_type_map['Uint'](self.context, 0, None)

		# Middle entry seemingly always 10^8, other two the same as LOD Distances
		self.unknown_values = Array(self.context, 0, None, (0,), name_type_map['Float'])

		# Entries corresponding to LODDistance specification in the block's NiStringExtraData, in the order of 1, 3, 2
		self.lod_distances = Array(self.context, 0, None, (0,), name_type_map['Float'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'unknown_bytes', Array, (0, None, (12,), name_type_map['Byte']), (False, None), (None, None)
		yield 'num_levels', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'unknown_values', Array, (0, None, (None,), name_type_map['Float']), (False, None), (None, None)
		yield 'lod_distances', Array, (0, None, (None,), name_type_map['Float']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'unknown_bytes', Array, (0, None, (12,), name_type_map['Byte']), (False, None)
		yield 'num_levels', name_type_map['Uint'], (0, None), (False, None)
		yield 'unknown_values', Array, (0, None, (instance.num_levels,), name_type_map['Float']), (False, None)
		yield 'lod_distances', Array, (0, None, (instance.num_levels,), name_type_map['Float']), (False, None)

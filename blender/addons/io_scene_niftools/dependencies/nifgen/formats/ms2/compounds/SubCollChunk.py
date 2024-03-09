from nifgen.array import Array
from nifgen.base_struct import BaseStruct
from nifgen.formats.ms2.imports import name_type_map


class SubCollChunk(BaseStruct):

	__name__ = 'SubCollChunk'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# verbatim
		self.bounds_min_repeat = name_type_map['Vector3'](self.context, 0, None)

		# verbatim
		self.bounds_max_repeat = name_type_map['Vector3'](self.context, 0, None)

		# seems to repeat tri_count
		self.tri_flags_count = name_type_map['Uint'](self.context, 0, None)

		# counts MeshCollisionBit
		self.count_bits = name_type_map['Ushort'](self.context, 0, None)

		# ?
		self.stuff = Array(self.context, 0, None, (0,), name_type_map['Ushort'])

		# ?
		self.collision_bits = Array(self.context, 0, None, (0,), name_type_map['MeshCollisionBit'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'bounds_min_repeat', name_type_map['Vector3'], (0, None), (False, None), (None, None)
		yield 'bounds_max_repeat', name_type_map['Vector3'], (0, None), (False, None), (None, None)
		yield 'tri_flags_count', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'count_bits', name_type_map['Ushort'], (0, None), (False, None), (None, None)
		yield 'stuff', Array, (0, None, (9,), name_type_map['Ushort']), (False, None), (None, None)
		yield 'collision_bits', Array, (0, None, (None,), name_type_map['MeshCollisionBit']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'bounds_min_repeat', name_type_map['Vector3'], (0, None), (False, None)
		yield 'bounds_max_repeat', name_type_map['Vector3'], (0, None), (False, None)
		yield 'tri_flags_count', name_type_map['Uint'], (0, None), (False, None)
		yield 'count_bits', name_type_map['Ushort'], (0, None), (False, None)
		yield 'stuff', Array, (0, None, (9,), name_type_map['Ushort']), (False, None)
		yield 'collision_bits', Array, (0, None, (instance.count_bits,), name_type_map['MeshCollisionBit']), (False, None)

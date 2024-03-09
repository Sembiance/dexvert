from nifgen.array import Array
from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nimain.niobjects.NiObject import NiObject


class NiBinaryVoxelData(NiObject):

	"""
	Voxel data object.
	"""

	__name__ = 'NiBinaryVoxelData'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.unknown_short_1 = name_type_map['Ushort'](self.context, 0, None)
		self.unknown_short_2 = name_type_map['Ushort'](self.context, 0, None)
		self.unknown_short_3 = name_type_map['Ushort'](self.context, 0, None)
		self.unknown_7_floats = Array(self.context, 0, None, (0,), name_type_map['Float'])
		self.unknown_bytes_1 = Array(self.context, 0, None, (0,), name_type_map['Byte'])
		self.num_unknown_vectors = name_type_map['Uint'](self.context, 0, None)
		self.unknown_vectors = Array(self.context, 0, None, (0,), name_type_map['Vector4'])
		self.num_unknown_bytes_2 = name_type_map['Uint'](self.context, 0, None)
		self.unknown_bytes_2 = Array(self.context, 0, None, (0,), name_type_map['Byte'])
		self.unknown_5_ints = Array(self.context, 0, None, (0,), name_type_map['Uint'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'unknown_short_1', name_type_map['Ushort'], (0, None), (False, None), (None, None)
		yield 'unknown_short_2', name_type_map['Ushort'], (0, None), (False, None), (None, None)
		yield 'unknown_short_3', name_type_map['Ushort'], (0, None), (False, None), (None, None)
		yield 'unknown_7_floats', Array, (0, None, (7,), name_type_map['Float']), (False, None), (None, None)
		yield 'unknown_bytes_1', Array, (0, None, (7, 12,), name_type_map['Byte']), (False, None), (None, None)
		yield 'num_unknown_vectors', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'unknown_vectors', Array, (0, None, (None,), name_type_map['Vector4']), (False, None), (None, None)
		yield 'num_unknown_bytes_2', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'unknown_bytes_2', Array, (0, None, (None,), name_type_map['Byte']), (False, None), (None, None)
		yield 'unknown_5_ints', Array, (0, None, (5,), name_type_map['Uint']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'unknown_short_1', name_type_map['Ushort'], (0, None), (False, None)
		yield 'unknown_short_2', name_type_map['Ushort'], (0, None), (False, None)
		yield 'unknown_short_3', name_type_map['Ushort'], (0, None), (False, None)
		yield 'unknown_7_floats', Array, (0, None, (7,), name_type_map['Float']), (False, None)
		yield 'unknown_bytes_1', Array, (0, None, (7, 12,), name_type_map['Byte']), (False, None)
		yield 'num_unknown_vectors', name_type_map['Uint'], (0, None), (False, None)
		yield 'unknown_vectors', Array, (0, None, (instance.num_unknown_vectors,), name_type_map['Vector4']), (False, None)
		yield 'num_unknown_bytes_2', name_type_map['Uint'], (0, None), (False, None)
		yield 'unknown_bytes_2', Array, (0, None, (instance.num_unknown_bytes_2,), name_type_map['Byte']), (False, None)
		yield 'unknown_5_ints', Array, (0, None, (5,), name_type_map['Uint']), (False, None)

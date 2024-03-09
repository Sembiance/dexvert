from nifgen.base_struct import BaseStruct
from nifgen.formats.ms2.imports import name_type_map


class TriChunk(BaseStruct):

	"""
	JWE2 Biosyn: 64 bytes
	"""

	__name__ = 'TriChunk'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# the smallest coordinates across all axes, min of unpacked vert coords if loc is 0,0,0
		self.bounds_min = name_type_map['Vector3'](self.context, 0, None)
		self.material_index = name_type_map['Ushort'](self.context, 0, None)
		self.tris_count = name_type_map['Ushort'](self.context, 0, None)

		# the biggest coordinates across all axes, max of unpacked vert coords if loc is 0,0,0
		self.bounds_max = name_type_map['Vector3'](self.context, 0, None)
		self.tris_offset = name_type_map['Uint'](self.context, 0, None)

		# can be 0,0,0, no obvious range, not always within range of bounds
		self.loc = name_type_map['Vector3'](self.context, 0, None)

		# can be 1, 0, 0, 0; w always in range -1, +1
		self.rot = name_type_map['AxisAngle'](self.context, 0, None)
		self.shell_index = name_type_map['Ushort'](self.context, 0, None)
		self.shell_count = name_type_map['Ushort'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'bounds_min', name_type_map['Vector3'], (0, None), (False, None), (None, None)
		yield 'material_index', name_type_map['Ushort'], (0, None), (False, None), (None, None)
		yield 'tris_count', name_type_map['Ushort'], (0, None), (False, None), (None, None)
		yield 'bounds_max', name_type_map['Vector3'], (0, None), (False, None), (None, None)
		yield 'tris_offset', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'loc', name_type_map['Vector3'], (0, None), (False, None), (None, None)
		yield 'rot', name_type_map['AxisAngle'], (0, None), (False, None), (None, None)
		yield 'shell_index', name_type_map['Ushort'], (0, None), (False, None), (None, None)
		yield 'shell_count', name_type_map['Ushort'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'bounds_min', name_type_map['Vector3'], (0, None), (False, None)
		yield 'material_index', name_type_map['Ushort'], (0, None), (False, None)
		yield 'tris_count', name_type_map['Ushort'], (0, None), (False, None)
		yield 'bounds_max', name_type_map['Vector3'], (0, None), (False, None)
		yield 'tris_offset', name_type_map['Uint'], (0, None), (False, None)
		yield 'loc', name_type_map['Vector3'], (0, None), (False, None)
		yield 'rot', name_type_map['AxisAngle'], (0, None), (False, None)
		yield 'shell_index', name_type_map['Ushort'], (0, None), (False, None)
		yield 'shell_count', name_type_map['Ushort'], (0, None), (False, None)

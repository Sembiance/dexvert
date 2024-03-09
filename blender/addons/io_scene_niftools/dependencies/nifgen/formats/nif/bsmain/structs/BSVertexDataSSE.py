from nifgen.array import Array
from nifgen.base_struct import BaseStruct
from nifgen.formats.nif.imports import name_type_map


class BSVertexDataSSE(BaseStruct):

	__name__ = 'BSVertexDataSSE'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.vertex = name_type_map['Vector3'](self.context, 0, None)
		self.bitangent_x = name_type_map['Float'](self.context, 0, None)
		self.unused_w = name_type_map['Uint'](self.context, 0, None)
		self.uv = name_type_map['HalfTexCoord'](self.context, 0, None)
		self.normal = name_type_map['ByteVector3'](self.context, 0, None)
		self.bitangent_y = name_type_map['Normbyte'](self.context, 0, None)
		self.tangent = name_type_map['ByteVector3'](self.context, 0, None)
		self.bitangent_z = name_type_map['Normbyte'](self.context, 0, None)
		self.vertex_colors = name_type_map['ByteColor4'](self.context, 0, None)
		self.bone_weights = Array(self.context, 0, None, (0,), name_type_map['Hfloat'])
		self.bone_indices = Array(self.context, 0, None, (0,), name_type_map['Byte'])
		self.eye_data = name_type_map['Float'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'vertex', name_type_map['Vector3'], (0, None), (False, None), (None, True)
		yield 'bitangent_x', name_type_map['Float'], (0, None), (False, None), (None, True)
		yield 'unused_w', name_type_map['Uint'], (0, None), (False, None), (None, True)
		yield 'uv', name_type_map['HalfTexCoord'], (0, None), (False, None), (None, True)
		yield 'normal', name_type_map['ByteVector3'], (0, None), (False, None), (None, True)
		yield 'bitangent_y', name_type_map['Normbyte'], (0, None), (False, None), (None, True)
		yield 'tangent', name_type_map['ByteVector3'], (0, None), (False, None), (None, True)
		yield 'bitangent_z', name_type_map['Normbyte'], (0, None), (False, None), (None, True)
		yield 'vertex_colors', name_type_map['ByteColor4'], (0, None), (False, None), (None, True)
		yield 'bone_weights', Array, (0, None, (4,), name_type_map['Hfloat']), (False, None), (None, True)
		yield 'bone_indices', Array, (0, None, (4,), name_type_map['Byte']), (False, None), (None, True)
		yield 'eye_data', name_type_map['Float'], (0, None), (False, None), (None, True)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		if (instance.arg & 1) != 0:
			yield 'vertex', name_type_map['Vector3'], (0, None), (False, None)
		if (instance.arg & 17) == 17:
			yield 'bitangent_x', name_type_map['Float'], (0, None), (False, None)
		if (instance.arg & 17) == 1:
			yield 'unused_w', name_type_map['Uint'], (0, None), (False, None)
		if (instance.arg & 2) != 0:
			yield 'uv', name_type_map['HalfTexCoord'], (0, None), (False, None)
		if (instance.arg & 8) != 0:
			yield 'normal', name_type_map['ByteVector3'], (0, None), (False, None)
			yield 'bitangent_y', name_type_map['Normbyte'], (0, None), (False, None)
		if (instance.arg & 24) == 24:
			yield 'tangent', name_type_map['ByteVector3'], (0, None), (False, None)
			yield 'bitangent_z', name_type_map['Normbyte'], (0, None), (False, None)
		if (instance.arg & 32) != 0:
			yield 'vertex_colors', name_type_map['ByteColor4'], (0, None), (False, None)
		if (instance.arg & 64) != 0:
			yield 'bone_weights', Array, (0, None, (4,), name_type_map['Hfloat']), (False, None)
			yield 'bone_indices', Array, (0, None, (4,), name_type_map['Byte']), (False, None)
		if (instance.arg & 256) != 0:
			yield 'eye_data', name_type_map['Float'], (0, None), (False, None)

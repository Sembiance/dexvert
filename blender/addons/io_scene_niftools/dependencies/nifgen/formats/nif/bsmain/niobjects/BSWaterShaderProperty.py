from nifgen.array import Array
from nifgen.formats.nif.bsmain.niobjects.BSShaderProperty import BSShaderProperty
from nifgen.formats.nif.imports import name_type_map


class BSWaterShaderProperty(BSShaderProperty):

	"""
	Skyrim water shader property, different from "WaterShaderProperty" seen in Fallout.
	"""

	__name__ = 'BSWaterShaderProperty'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.shader_flags_1 = name_type_map['SkyrimShaderPropertyFlags1'].from_value(2147483656)
		self.shader_flags_2 = name_type_map['SkyrimShaderPropertyFlags2'].from_value(33)
		self.num_sf_1 = name_type_map['Uint'](self.context, 0, None)
		self.num_sf_2 = name_type_map['Uint'](self.context, 0, None)
		self.sf_1 = Array(self.context, 0, None, (0,), name_type_map['BSShaderCRC32'])
		self.sf_2 = Array(self.context, 0, None, (0,), name_type_map['BSShaderCRC32'])

		# Offset UVs. Seems to be unused, but it fits with the other Skyrim shader properties.
		self.uv_offset = name_type_map['TexCoord'](self.context, 0, None)

		# Offset UV Scale to repeat tiling textures, see above.
		self.uv_scale = name_type_map['TexCoord'].from_value((1.0, 1.0))
		self.water_shader_flags = name_type_map['WaterShaderPropertyFlags'].from_value(196)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'shader_flags_1', name_type_map['SkyrimShaderPropertyFlags1'], (0, None), (False, 2147483656), (lambda context: not (context.bs_header.bs_version >= 132), None)
		yield 'shader_flags_2', name_type_map['SkyrimShaderPropertyFlags2'], (0, None), (False, 33), (lambda context: not (context.bs_header.bs_version >= 132), None)
		yield 'num_sf_1', name_type_map['Uint'], (0, None), (False, None), (lambda context: context.bs_header.bs_version >= 132, None)
		yield 'num_sf_2', name_type_map['Uint'], (0, None), (False, None), (lambda context: context.bs_header.bs_version >= 152, None)
		yield 'sf_1', Array, (0, None, (None,), name_type_map['BSShaderCRC32']), (False, None), (lambda context: context.bs_header.bs_version >= 132, None)
		yield 'sf_2', Array, (0, None, (None,), name_type_map['BSShaderCRC32']), (False, None), (lambda context: context.bs_header.bs_version >= 152, None)
		yield 'uv_offset', name_type_map['TexCoord'], (0, None), (False, None), (None, None)
		yield 'uv_scale', name_type_map['TexCoord'], (0, None), (False, (1.0, 1.0)), (None, None)
		yield 'water_shader_flags', name_type_map['WaterShaderPropertyFlags'], (0, None), (False, 196), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		if not (instance.context.bs_header.bs_version >= 132):
			yield 'shader_flags_1', name_type_map['SkyrimShaderPropertyFlags1'], (0, None), (False, 2147483656)
			yield 'shader_flags_2', name_type_map['SkyrimShaderPropertyFlags2'], (0, None), (False, 33)
		if instance.context.bs_header.bs_version >= 132:
			yield 'num_sf_1', name_type_map['Uint'], (0, None), (False, None)
		if instance.context.bs_header.bs_version >= 152:
			yield 'num_sf_2', name_type_map['Uint'], (0, None), (False, None)
		if instance.context.bs_header.bs_version >= 132:
			yield 'sf_1', Array, (0, None, (instance.num_sf_1,), name_type_map['BSShaderCRC32']), (False, None)
		if instance.context.bs_header.bs_version >= 152:
			yield 'sf_2', Array, (0, None, (instance.num_sf_2,), name_type_map['BSShaderCRC32']), (False, None)
		yield 'uv_offset', name_type_map['TexCoord'], (0, None), (False, None)
		yield 'uv_scale', name_type_map['TexCoord'], (0, None), (False, (1.0, 1.0))
		yield 'water_shader_flags', name_type_map['WaterShaderPropertyFlags'], (0, None), (False, 196)

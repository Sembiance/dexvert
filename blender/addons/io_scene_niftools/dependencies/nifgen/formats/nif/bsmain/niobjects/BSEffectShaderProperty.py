from nifgen.array import Array
from nifgen.formats.nif.bsmain.niobjects.BSShaderProperty import BSShaderProperty
from nifgen.formats.nif.imports import name_type_map


class BSEffectShaderProperty(BSShaderProperty):

	"""
	Bethesda effect shader property for Skyrim and later.
	"""

	__name__ = 'BSEffectShaderProperty'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.shader_flags_1 = name_type_map['SkyrimShaderPropertyFlags1'].from_value(2147483648)
		self.shader_flags_2 = name_type_map['SkyrimShaderPropertyFlags2'].from_value(32)
		self.shader_flags_1 = name_type_map['Fallout4ShaderPropertyFlags1'].from_value(2147483648)
		self.shader_flags_2 = name_type_map['Fallout4ShaderPropertyFlags2'].from_value(32)
		self.num_sf_1 = name_type_map['Uint'](self.context, 0, None)
		self.num_sf_2 = name_type_map['Uint'](self.context, 0, None)
		self.sf_1 = Array(self.context, 0, None, (0,), name_type_map['BSShaderCRC32'])
		self.sf_2 = Array(self.context, 0, None, (0,), name_type_map['BSShaderCRC32'])

		# Offset UVs
		self.uv_offset = name_type_map['TexCoord'](self.context, 0, None)

		# Offset UV Scale to repeat tiling textures
		self.uv_scale = name_type_map['TexCoord'].from_value((1.0, 1.0))

		# points to an external texture.
		self.source_texture = name_type_map['SizedString'](self.context, 0, None)

		# How to handle texture borders.
		self.texture_clamp_mode = name_type_map['Byte'].from_value(3)
		self.lighting_influence = name_type_map['Byte'].from_value(255)
		self.env_map_min_lod = name_type_map['Byte'](self.context, 0, None)
		self.unused_byte = name_type_map['Byte'](self.context, 0, None)

		# At this cosine of angle falloff will be equal to Falloff Start Opacity
		self.falloff_start_angle = name_type_map['Float'].from_value(1.0)

		# At this cosine of angle falloff will be equal to Falloff Stop Opacity
		self.falloff_stop_angle = name_type_map['Float'].from_value(1.0)

		# Alpha falloff multiplier at start angle
		self.falloff_start_opacity = name_type_map['Float'](self.context, 0, None)

		# Alpha falloff multiplier at end angle
		self.falloff_stop_opacity = name_type_map['Float'](self.context, 0, None)
		self.refraction_power = name_type_map['Float'](self.context, 0, None)

		# Base color
		self.base_color = name_type_map['Color4'].from_value((1.0, 1.0, 1.0, 1.0))

		# Multiplier for Base Color (RGB part)
		self.base_color_scale = name_type_map['Float'].from_value(1.0)
		self.soft_falloff_depth = name_type_map['Float'].from_value(100.0)

		# Points to an external texture, used as palette for SLSF1_Greyscale_To_PaletteColor/SLSF1_Greyscale_To_PaletteAlpha.
		self.greyscale_texture = name_type_map['SizedString'](self.context, 0, None)
		self.env_map_texture = name_type_map['SizedString'](self.context, 0, None)
		self.normal_texture = name_type_map['SizedString'](self.context, 0, None)
		self.env_mask_texture = name_type_map['SizedString'](self.context, 0, None)
		self.environment_map_scale = name_type_map['Float'].from_value(1.0)
		self.reflectance_texture = name_type_map['SizedString'](self.context, 0, None)
		self.lighting_texture = name_type_map['SizedString'](self.context, 0, None)
		self.emittance_color = name_type_map['Color3'](self.context, 0, None)
		self.emit_gradient_texture = name_type_map['SizedString'](self.context, 0, None)
		self.luminance = name_type_map['BSSPLuminanceParams'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'shader_flags_1', name_type_map['SkyrimShaderPropertyFlags1'], (0, None), (False, 2147483648), (lambda context: context.bs_header.bs_version < 130, None)
		yield 'shader_flags_2', name_type_map['SkyrimShaderPropertyFlags2'], (0, None), (False, 32), (lambda context: context.bs_header.bs_version < 130, None)
		yield 'shader_flags_1', name_type_map['Fallout4ShaderPropertyFlags1'], (0, None), (False, 2147483648), (lambda context: context.bs_header.bs_version == 130, None)
		yield 'shader_flags_2', name_type_map['Fallout4ShaderPropertyFlags2'], (0, None), (False, 32), (lambda context: context.bs_header.bs_version == 130, None)
		yield 'num_sf_1', name_type_map['Uint'], (0, None), (False, None), (lambda context: context.bs_header.bs_version >= 132, None)
		yield 'num_sf_2', name_type_map['Uint'], (0, None), (False, None), (lambda context: context.bs_header.bs_version >= 152, None)
		yield 'sf_1', Array, (0, None, (None,), name_type_map['BSShaderCRC32']), (False, None), (lambda context: context.bs_header.bs_version >= 132, None)
		yield 'sf_2', Array, (0, None, (None,), name_type_map['BSShaderCRC32']), (False, None), (lambda context: context.bs_header.bs_version >= 152, None)
		yield 'uv_offset', name_type_map['TexCoord'], (0, None), (False, None), (None, None)
		yield 'uv_scale', name_type_map['TexCoord'], (0, None), (False, (1.0, 1.0)), (None, None)
		yield 'source_texture', name_type_map['SizedString'], (0, None), (False, None), (None, None)
		yield 'texture_clamp_mode', name_type_map['Byte'], (0, None), (False, 3), (None, None)
		yield 'lighting_influence', name_type_map['Byte'], (0, None), (False, 255), (None, None)
		yield 'env_map_min_lod', name_type_map['Byte'], (0, None), (False, None), (None, None)
		yield 'unused_byte', name_type_map['Byte'], (0, None), (False, None), (None, None)
		yield 'falloff_start_angle', name_type_map['Float'], (0, None), (False, 1.0), (None, None)
		yield 'falloff_stop_angle', name_type_map['Float'], (0, None), (False, 1.0), (None, None)
		yield 'falloff_start_opacity', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'falloff_stop_opacity', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'refraction_power', name_type_map['Float'], (0, None), (False, None), (lambda context: context.bs_header.bs_version == 155, None)
		yield 'base_color', name_type_map['Color4'], (0, None), (False, (1.0, 1.0, 1.0, 1.0)), (None, None)
		yield 'base_color_scale', name_type_map['Float'], (0, None), (False, 1.0), (None, None)
		yield 'soft_falloff_depth', name_type_map['Float'], (0, None), (False, 100.0), (None, None)
		yield 'greyscale_texture', name_type_map['SizedString'], (0, None), (False, None), (None, None)
		yield 'env_map_texture', name_type_map['SizedString'], (0, None), (False, None), (lambda context: context.bs_header.bs_version >= 130, None)
		yield 'normal_texture', name_type_map['SizedString'], (0, None), (False, None), (lambda context: context.bs_header.bs_version >= 130, None)
		yield 'env_mask_texture', name_type_map['SizedString'], (0, None), (False, None), (lambda context: context.bs_header.bs_version >= 130, None)
		yield 'environment_map_scale', name_type_map['Float'], (0, None), (False, 1.0), (lambda context: context.bs_header.bs_version >= 130, None)
		yield 'reflectance_texture', name_type_map['SizedString'], (0, None), (False, None), (lambda context: context.bs_header.bs_version == 155, None)
		yield 'lighting_texture', name_type_map['SizedString'], (0, None), (False, None), (lambda context: context.bs_header.bs_version == 155, None)
		yield 'emittance_color', name_type_map['Color3'], (0, None), (False, None), (lambda context: context.bs_header.bs_version == 155, None)
		yield 'emit_gradient_texture', name_type_map['SizedString'], (0, None), (False, None), (lambda context: context.bs_header.bs_version == 155, None)
		yield 'luminance', name_type_map['BSSPLuminanceParams'], (0, None), (False, None), (lambda context: context.bs_header.bs_version == 155, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		if instance.context.bs_header.bs_version < 130:
			yield 'shader_flags_1', name_type_map['SkyrimShaderPropertyFlags1'], (0, None), (False, 2147483648)
			yield 'shader_flags_2', name_type_map['SkyrimShaderPropertyFlags2'], (0, None), (False, 32)
		if instance.context.bs_header.bs_version == 130:
			yield 'shader_flags_1', name_type_map['Fallout4ShaderPropertyFlags1'], (0, None), (False, 2147483648)
			yield 'shader_flags_2', name_type_map['Fallout4ShaderPropertyFlags2'], (0, None), (False, 32)
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
		yield 'source_texture', name_type_map['SizedString'], (0, None), (False, None)
		yield 'texture_clamp_mode', name_type_map['Byte'], (0, None), (False, 3)
		yield 'lighting_influence', name_type_map['Byte'], (0, None), (False, 255)
		yield 'env_map_min_lod', name_type_map['Byte'], (0, None), (False, None)
		yield 'unused_byte', name_type_map['Byte'], (0, None), (False, None)
		yield 'falloff_start_angle', name_type_map['Float'], (0, None), (False, 1.0)
		yield 'falloff_stop_angle', name_type_map['Float'], (0, None), (False, 1.0)
		yield 'falloff_start_opacity', name_type_map['Float'], (0, None), (False, None)
		yield 'falloff_stop_opacity', name_type_map['Float'], (0, None), (False, None)
		if instance.context.bs_header.bs_version == 155:
			yield 'refraction_power', name_type_map['Float'], (0, None), (False, None)
		yield 'base_color', name_type_map['Color4'], (0, None), (False, (1.0, 1.0, 1.0, 1.0))
		yield 'base_color_scale', name_type_map['Float'], (0, None), (False, 1.0)
		yield 'soft_falloff_depth', name_type_map['Float'], (0, None), (False, 100.0)
		yield 'greyscale_texture', name_type_map['SizedString'], (0, None), (False, None)
		if instance.context.bs_header.bs_version >= 130:
			yield 'env_map_texture', name_type_map['SizedString'], (0, None), (False, None)
			yield 'normal_texture', name_type_map['SizedString'], (0, None), (False, None)
			yield 'env_mask_texture', name_type_map['SizedString'], (0, None), (False, None)
			yield 'environment_map_scale', name_type_map['Float'], (0, None), (False, 1.0)
		if instance.context.bs_header.bs_version == 155:
			yield 'reflectance_texture', name_type_map['SizedString'], (0, None), (False, None)
			yield 'lighting_texture', name_type_map['SizedString'], (0, None), (False, None)
			yield 'emittance_color', name_type_map['Color3'], (0, None), (False, None)
			yield 'emit_gradient_texture', name_type_map['SizedString'], (0, None), (False, None)
			yield 'luminance', name_type_map['BSSPLuminanceParams'], (0, None), (False, None)

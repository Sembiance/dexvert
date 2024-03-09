from nifgen.array import Array
from nifgen.formats.nif.bsmain.niobjects.BSShaderProperty import BSShaderProperty
from nifgen.formats.nif.imports import name_type_map


class BSLightingShaderProperty(BSShaderProperty):

	"""
	Bethesda shader property for Skyrim and later.
	"""

	__name__ = 'BSLightingShaderProperty'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# Skyrim Shader Flags for setting render/shader options.
		self.shader_flags_1 = name_type_map['SkyrimShaderPropertyFlags1'].from_value(2185233153)

		# Skyrim Shader Flags for setting render/shader options.
		self.shader_flags_2 = name_type_map['SkyrimShaderPropertyFlags2'].from_value(32801)

		# Fallout 4 Shader Flags. Mostly overridden if "Name" is a path to a BGSM/BGEM file.
		self.shader_flags_1 = name_type_map['Fallout4ShaderPropertyFlags1'].from_value(2151678465)

		# Fallout 4 Shader Flags. Mostly overridden if "Name" is a path to a BGSM/BGEM file.
		self.shader_flags_2 = name_type_map['Fallout4ShaderPropertyFlags2'].from_value(1)
		self.shader_type = name_type_map['BSShaderType155'](self.context, 0, None)
		self.num_sf_1 = name_type_map['Uint'](self.context, 0, None)
		self.num_sf_2 = name_type_map['Uint'](self.context, 0, None)
		self.sf_1 = Array(self.context, 0, None, (0,), name_type_map['BSShaderCRC32'])
		self.sf_2 = Array(self.context, 0, None, (0,), name_type_map['BSShaderCRC32'])

		# Offset UVs
		self.uv_offset = name_type_map['TexCoord'](self.context, 0, None)

		# Offset UV Scale to repeat tiling textures, see above.
		self.uv_scale = name_type_map['TexCoord'].from_value((1.0, 1.0))

		# Texture Set, can have override in an esm/esp
		self.texture_set = name_type_map['Ref'](self.context, 0, name_type_map['BSShaderTextureSet'])

		# Glow color and alpha
		self.emissive_color = name_type_map['Color3'].from_value((0.0, 0.0, 0.0))

		# Multiplied emissive colors
		self.emissive_multiple = name_type_map['Float'].from_value(1.0)
		self.root_material = name_type_map['NiFixedString'](self.context, 0, None)

		# How to handle texture borders.
		self.texture_clamp_mode = name_type_map['TexClampMode'].WRAP_S_WRAP_T

		# The material opacity (1=opaque). Greater than 1.0 is used to affect alpha falloff i.e. staying opaque longer based on vertex alpha and alpha mask.
		self.alpha = name_type_map['Float'].from_value(1.0)

		# The amount of distortion. **Not based on physically accurate refractive index** (0=none)
		self.refraction_strength = name_type_map['Float'](self.context, 0, None)

		# The material specular power, or glossiness.
		self.glossiness = name_type_map['Float'].from_value(80.0)

		# The base roughness, multiplied by the smoothness map.
		self.smoothness = name_type_map['Float'].from_value(1.0)

		# Adds a colored highlight.
		self.specular_color = name_type_map['Color3'].from_value((1.0, 1.0, 1.0))

		# Brightness of specular highlight. (0=not visible)
		self.specular_strength = name_type_map['Float'].from_value(1.0)

		# Controls strength for envmap/backlight/rim/softlight lighting effect?
		self.lighting_effect_1 = name_type_map['Float'].from_value(0.3)

		# Controls strength for envmap/backlight/rim/softlight lighting effect?
		self.lighting_effect_2 = name_type_map['Float'].from_value(2.0)
		self.subsurface_rolloff = name_type_map['Float'].from_value(0.0)
		self.rimlight_power = name_type_map['Float'].from_value(3.402823466e+38)
		self.backlight_power = name_type_map['Float'](self.context, 0, None)
		self.grayscale_to_palette_scale = name_type_map['Float'].from_value(1.0)
		self.fresnel_power = name_type_map['Float'].from_value(5.0)
		self.wetness = name_type_map['BSSPWetnessParams'](self.context, 0, None)
		self.luminance = name_type_map['BSSPLuminanceParams'](self.context, 0, None)
		self.do_translucency = name_type_map['Bool'](self.context, 0, None)
		self.translucency = name_type_map['BSSPTranslucencyParams'](self.context, 0, None)
		self.has_texture_arrays = name_type_map['Byte'](self.context, 0, None)
		self.num_texture_arrays = name_type_map['Uint'](self.context, 0, None)
		self.texture_arrays = Array(self.context, 0, None, (0,), name_type_map['BSTextureArray'])

		# Scales the intensity of the environment/cube map.
		self.environment_map_scale = name_type_map['Float'].from_value(1.0)
		self.use_screen_space_reflections = name_type_map['Bool'](self.context, 0, None)
		self.wetness_control_use_ssr = name_type_map['Bool'](self.context, 0, None)
		self.skin_tint_color = name_type_map['Color4'](self.context, 0, None)
		self.hair_tint_color = name_type_map['Color3'](self.context, 0, None)

		# Tints the base texture. Overridden by game settings.
		self.skin_tint_color = name_type_map['Color3'].from_value((1.0, 1.0, 1.0))
		self.skin_tint_alpha = name_type_map['Float'].from_value(1.0)

		# Tints the base texture. Overridden by game settings.
		self.hair_tint_color = name_type_map['Color3'].from_value((1.0, 1.0, 1.0))
		self.max_passes = name_type_map['Float'].from_value(4.0)
		self.scale = name_type_map['Float'].from_value(1.0)

		# How far from the surface the inner layer appears to be.
		self.parallax_inner_layer_thickness = name_type_map['Float'].from_value(5.0)

		# Depth of inner parallax layer effect.
		self.parallax_refraction_scale = name_type_map['Float'].from_value(0.25)

		# Scales the inner parallax layer texture.
		self.parallax_inner_layer_texture_scale = name_type_map['TexCoord'](self.context, 0, None)

		# How strong the environment/cube map is.
		self.parallax_envmap_strength = name_type_map['Float'].from_value(1.0)

		# CK lists "snow material" when used.
		self.sparkle_parameters = name_type_map['Vector4'](self.context, 0, None)

		# Eye cubemap scale
		self.eye_cubemap_scale = name_type_map['Float'].from_value(1.3)

		# Offset to set center for left eye cubemap
		self.left_eye_reflection_center = name_type_map['Vector3'](self.context, 0, None)

		# Offset to set center for right eye cubemap
		self.right_eye_reflection_center = name_type_map['Vector3'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'shader_flags_1', name_type_map['SkyrimShaderPropertyFlags1'], (0, None), (False, 2185233153), (lambda context: context.bs_header.bs_version < 130, None)
		yield 'shader_flags_2', name_type_map['SkyrimShaderPropertyFlags2'], (0, None), (False, 32801), (lambda context: context.bs_header.bs_version < 130, None)
		yield 'shader_flags_1', name_type_map['Fallout4ShaderPropertyFlags1'], (0, None), (False, 2151678465), (lambda context: context.bs_header.bs_version == 130, None)
		yield 'shader_flags_2', name_type_map['Fallout4ShaderPropertyFlags2'], (0, None), (False, 1), (lambda context: context.bs_header.bs_version == 130, None)
		yield 'shader_type', name_type_map['BSShaderType155'], (0, None), (False, None), (lambda context: context.bs_header.bs_version == 155, None)
		yield 'num_sf_1', name_type_map['Uint'], (0, None), (False, None), (lambda context: context.bs_header.bs_version >= 132, None)
		yield 'num_sf_2', name_type_map['Uint'], (0, None), (False, None), (lambda context: context.bs_header.bs_version >= 152, None)
		yield 'sf_1', Array, (0, None, (None,), name_type_map['BSShaderCRC32']), (False, None), (lambda context: context.bs_header.bs_version >= 132, None)
		yield 'sf_2', Array, (0, None, (None,), name_type_map['BSShaderCRC32']), (False, None), (lambda context: context.bs_header.bs_version >= 152, None)
		yield 'uv_offset', name_type_map['TexCoord'], (0, None), (False, None), (None, None)
		yield 'uv_scale', name_type_map['TexCoord'], (0, None), (False, (1.0, 1.0)), (None, None)
		yield 'texture_set', name_type_map['Ref'], (0, name_type_map['BSShaderTextureSet']), (False, None), (None, None)
		yield 'emissive_color', name_type_map['Color3'], (0, None), (False, (0.0, 0.0, 0.0)), (None, None)
		yield 'emissive_multiple', name_type_map['Float'], (0, None), (False, 1.0), (None, None)
		yield 'root_material', name_type_map['NiFixedString'], (0, None), (False, None), (lambda context: context.bs_header.bs_version >= 130, None)
		yield 'texture_clamp_mode', name_type_map['TexClampMode'], (0, None), (False, name_type_map['TexClampMode'].WRAP_S_WRAP_T), (None, None)
		yield 'alpha', name_type_map['Float'], (0, None), (False, 1.0), (None, None)
		yield 'refraction_strength', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'glossiness', name_type_map['Float'], (0, None), (False, 80.0), (lambda context: context.bs_header.bs_version < 130, None)
		yield 'smoothness', name_type_map['Float'], (0, None), (False, 1.0), (lambda context: context.bs_header.bs_version >= 130, None)
		yield 'specular_color', name_type_map['Color3'], (0, None), (False, (1.0, 1.0, 1.0)), (None, None)
		yield 'specular_strength', name_type_map['Float'], (0, None), (False, 1.0), (None, None)
		yield 'lighting_effect_1', name_type_map['Float'], (0, None), (False, 0.3), (lambda context: context.bs_header.bs_version < 130, None)
		yield 'lighting_effect_2', name_type_map['Float'], (0, None), (False, 2.0), (lambda context: context.bs_header.bs_version < 130, None)
		yield 'subsurface_rolloff', name_type_map['Float'], (0, None), (False, 0.0), (lambda context: (context.bs_header.bs_version >= 130) and (context.bs_header.bs_version <= 139), None)
		yield 'rimlight_power', name_type_map['Float'], (0, None), (False, 3.402823466e+38), (lambda context: (context.bs_header.bs_version >= 130) and (context.bs_header.bs_version <= 139), None)
		yield 'backlight_power', name_type_map['Float'], (0, None), (False, None), (lambda context: (context.bs_header.bs_version >= 130) and (context.bs_header.bs_version <= 139), True)
		yield 'grayscale_to_palette_scale', name_type_map['Float'], (0, None), (False, 1.0), (lambda context: context.bs_header.bs_version >= 130, None)
		yield 'fresnel_power', name_type_map['Float'], (0, None), (False, 5.0), (lambda context: context.bs_header.bs_version >= 130, None)
		yield 'wetness', name_type_map['BSSPWetnessParams'], (0, None), (False, None), (lambda context: context.bs_header.bs_version >= 130, None)
		yield 'luminance', name_type_map['BSSPLuminanceParams'], (0, None), (False, None), (lambda context: context.bs_header.bs_version == 155, None)
		yield 'do_translucency', name_type_map['Bool'], (0, None), (False, None), (lambda context: context.bs_header.bs_version == 155, None)
		yield 'translucency', name_type_map['BSSPTranslucencyParams'], (0, None), (False, None), (lambda context: context.bs_header.bs_version == 155, True)
		yield 'has_texture_arrays', name_type_map['Byte'], (0, None), (False, None), (lambda context: context.bs_header.bs_version == 155, None)
		yield 'num_texture_arrays', name_type_map['Uint'], (0, None), (False, None), (lambda context: context.bs_header.bs_version == 155, True)
		yield 'texture_arrays', Array, (0, None, (None,), name_type_map['BSTextureArray']), (False, None), (lambda context: context.bs_header.bs_version == 155, True)
		yield 'environment_map_scale', name_type_map['Float'], (0, None), (False, 1.0), (lambda context: context.bs_header.bs_version <= 139, True)
		yield 'use_screen_space_reflections', name_type_map['Bool'], (0, None), (False, None), (lambda context: (context.bs_header.bs_version >= 130) and (context.bs_header.bs_version <= 139), True)
		yield 'wetness_control_use_ssr', name_type_map['Bool'], (0, None), (False, None), (lambda context: (context.bs_header.bs_version >= 130) and (context.bs_header.bs_version <= 139), True)
		yield 'skin_tint_color', name_type_map['Color4'], (0, None), (False, None), (lambda context: context.bs_header.bs_version == 155, True)
		yield 'hair_tint_color', name_type_map['Color3'], (0, None), (False, None), (lambda context: context.bs_header.bs_version == 155, True)
		yield 'skin_tint_color', name_type_map['Color3'], (0, None), (False, (1.0, 1.0, 1.0)), (lambda context: context.bs_header.bs_version <= 139, True)
		yield 'skin_tint_alpha', name_type_map['Float'], (0, None), (False, 1.0), (lambda context: (context.bs_header.bs_version >= 130) and (context.bs_header.bs_version <= 139), True)
		yield 'hair_tint_color', name_type_map['Color3'], (0, None), (False, (1.0, 1.0, 1.0)), (lambda context: context.bs_header.bs_version <= 139, True)
		yield 'max_passes', name_type_map['Float'], (0, None), (False, 4.0), (None, True)
		yield 'scale', name_type_map['Float'], (0, None), (False, 1.0), (None, True)
		yield 'parallax_inner_layer_thickness', name_type_map['Float'], (0, None), (False, 5.0), (None, True)
		yield 'parallax_refraction_scale', name_type_map['Float'], (0, None), (False, 0.25), (None, True)
		yield 'parallax_inner_layer_texture_scale', name_type_map['TexCoord'], (0, None), (False, None), (None, True)
		yield 'parallax_envmap_strength', name_type_map['Float'], (0, None), (False, 1.0), (None, True)
		yield 'sparkle_parameters', name_type_map['Vector4'], (0, None), (False, None), (None, True)
		yield 'eye_cubemap_scale', name_type_map['Float'], (0, None), (False, 1.3), (None, True)
		yield 'left_eye_reflection_center', name_type_map['Vector3'], (0, None), (False, None), (None, True)
		yield 'right_eye_reflection_center', name_type_map['Vector3'], (0, None), (False, None), (None, True)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		if instance.context.bs_header.bs_version < 130:
			yield 'shader_flags_1', name_type_map['SkyrimShaderPropertyFlags1'], (0, None), (False, 2185233153)
			yield 'shader_flags_2', name_type_map['SkyrimShaderPropertyFlags2'], (0, None), (False, 32801)
		if instance.context.bs_header.bs_version == 130:
			yield 'shader_flags_1', name_type_map['Fallout4ShaderPropertyFlags1'], (0, None), (False, 2151678465)
			yield 'shader_flags_2', name_type_map['Fallout4ShaderPropertyFlags2'], (0, None), (False, 1)
		if instance.context.bs_header.bs_version == 155:
			yield 'shader_type', name_type_map['BSShaderType155'], (0, None), (False, None)
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
		yield 'texture_set', name_type_map['Ref'], (0, name_type_map['BSShaderTextureSet']), (False, None)
		yield 'emissive_color', name_type_map['Color3'], (0, None), (False, (0.0, 0.0, 0.0))
		yield 'emissive_multiple', name_type_map['Float'], (0, None), (False, 1.0)
		if instance.context.bs_header.bs_version >= 130:
			yield 'root_material', name_type_map['NiFixedString'], (0, None), (False, None)
		yield 'texture_clamp_mode', name_type_map['TexClampMode'], (0, None), (False, name_type_map['TexClampMode'].WRAP_S_WRAP_T)
		yield 'alpha', name_type_map['Float'], (0, None), (False, 1.0)
		yield 'refraction_strength', name_type_map['Float'], (0, None), (False, None)
		if instance.context.bs_header.bs_version < 130:
			yield 'glossiness', name_type_map['Float'], (0, None), (False, 80.0)
		if instance.context.bs_header.bs_version >= 130:
			yield 'smoothness', name_type_map['Float'], (0, None), (False, 1.0)
		yield 'specular_color', name_type_map['Color3'], (0, None), (False, (1.0, 1.0, 1.0))
		yield 'specular_strength', name_type_map['Float'], (0, None), (False, 1.0)
		if instance.context.bs_header.bs_version < 130:
			yield 'lighting_effect_1', name_type_map['Float'], (0, None), (False, 0.3)
			yield 'lighting_effect_2', name_type_map['Float'], (0, None), (False, 2.0)
		if (instance.context.bs_header.bs_version >= 130) and (instance.context.bs_header.bs_version <= 139):
			yield 'subsurface_rolloff', name_type_map['Float'], (0, None), (False, 0.0)
			yield 'rimlight_power', name_type_map['Float'], (0, None), (False, 3.402823466e+38)
		if (instance.context.bs_header.bs_version >= 130) and (instance.context.bs_header.bs_version <= 139) and (instance.rimlight_power >= 3.402823466e+38) and (instance.rimlight_power < float('inf')):
			yield 'backlight_power', name_type_map['Float'], (0, None), (False, None)
		if instance.context.bs_header.bs_version >= 130:
			yield 'grayscale_to_palette_scale', name_type_map['Float'], (0, None), (False, 1.0)
			yield 'fresnel_power', name_type_map['Float'], (0, None), (False, 5.0)
			yield 'wetness', name_type_map['BSSPWetnessParams'], (0, None), (False, None)
		if instance.context.bs_header.bs_version == 155:
			yield 'luminance', name_type_map['BSSPLuminanceParams'], (0, None), (False, None)
			yield 'do_translucency', name_type_map['Bool'], (0, None), (False, None)
		if instance.context.bs_header.bs_version == 155 and instance.do_translucency:
			yield 'translucency', name_type_map['BSSPTranslucencyParams'], (0, None), (False, None)
		if instance.context.bs_header.bs_version == 155:
			yield 'has_texture_arrays', name_type_map['Byte'], (0, None), (False, None)
		if instance.context.bs_header.bs_version == 155 and instance.has_texture_arrays:
			yield 'num_texture_arrays', name_type_map['Uint'], (0, None), (False, None)
			yield 'texture_arrays', Array, (0, None, (instance.num_texture_arrays,), name_type_map['BSTextureArray']), (False, None)
		if instance.context.bs_header.bs_version <= 139 and instance.shader_type == 1:
			yield 'environment_map_scale', name_type_map['Float'], (0, None), (False, 1.0)
		if (instance.context.bs_header.bs_version >= 130) and (instance.context.bs_header.bs_version <= 139) and instance.shader_type == 1:
			yield 'use_screen_space_reflections', name_type_map['Bool'], (0, None), (False, None)
			yield 'wetness_control_use_ssr', name_type_map['Bool'], (0, None), (False, None)
		if instance.context.bs_header.bs_version == 155 and instance.shader_type == 4:
			yield 'skin_tint_color', name_type_map['Color4'], (0, None), (False, None)
		if instance.context.bs_header.bs_version == 155 and instance.shader_type == 5:
			yield 'hair_tint_color', name_type_map['Color3'], (0, None), (False, None)
		if instance.context.bs_header.bs_version <= 139 and instance.shader_type == 5:
			yield 'skin_tint_color', name_type_map['Color3'], (0, None), (False, (1.0, 1.0, 1.0))
		if (instance.context.bs_header.bs_version >= 130) and (instance.context.bs_header.bs_version <= 139) and instance.shader_type == 5:
			yield 'skin_tint_alpha', name_type_map['Float'], (0, None), (False, 1.0)
		if instance.context.bs_header.bs_version <= 139 and instance.shader_type == 6:
			yield 'hair_tint_color', name_type_map['Color3'], (0, None), (False, (1.0, 1.0, 1.0))
		if instance.shader_type == 7:
			yield 'max_passes', name_type_map['Float'], (0, None), (False, 4.0)
			yield 'scale', name_type_map['Float'], (0, None), (False, 1.0)
		if instance.shader_type == 11:
			yield 'parallax_inner_layer_thickness', name_type_map['Float'], (0, None), (False, 5.0)
			yield 'parallax_refraction_scale', name_type_map['Float'], (0, None), (False, 0.25)
			yield 'parallax_inner_layer_texture_scale', name_type_map['TexCoord'], (0, None), (False, None)
			yield 'parallax_envmap_strength', name_type_map['Float'], (0, None), (False, 1.0)
		if instance.shader_type == 14:
			yield 'sparkle_parameters', name_type_map['Vector4'], (0, None), (False, None)
		if instance.shader_type == 16:
			yield 'eye_cubemap_scale', name_type_map['Float'], (0, None), (False, 1.3)
			yield 'left_eye_reflection_center', name_type_map['Vector3'], (0, None), (False, None)
			yield 'right_eye_reflection_center', name_type_map['Vector3'], (0, None), (False, None)

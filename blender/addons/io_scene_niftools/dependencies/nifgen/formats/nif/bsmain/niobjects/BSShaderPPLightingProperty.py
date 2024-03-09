from nifgen.formats.nif.bsmain.niobjects.BSShaderLightingProperty import BSShaderLightingProperty
from nifgen.formats.nif.imports import name_type_map


class BSShaderPPLightingProperty(BSShaderLightingProperty):

	"""
	Bethesda-specific property.
	"""

	__name__ = 'BSShaderPPLightingProperty'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# Texture Set
		self.texture_set = name_type_map['Ref'](self.context, 0, name_type_map['BSShaderTextureSet'])

		# The amount of distortion. **Not based on physically accurate refractive index** (0=none) (0-1)
		self.refraction_strength = name_type_map['Float'].from_value(0.0)

		# Rate of texture movement for refraction shader.
		self.refraction_fire_period = name_type_map['Int'].from_value(0)

		# The number of passes the parallax shader can apply.
		self.parallax_max_passes = name_type_map['Float'].from_value(4.0)

		# The strength of the parallax.
		self.parallax_scale = name_type_map['Float'].from_value(1.0)

		# Glow color and alpha
		self.emissive_color = name_type_map['Color4'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'texture_set', name_type_map['Ref'], (0, name_type_map['BSShaderTextureSet']), (False, None), (None, None)
		yield 'refraction_strength', name_type_map['Float'], (0, None), (False, 0.0), (lambda context: context.bs_header.bs_version > 14, None)
		yield 'refraction_fire_period', name_type_map['Int'], (0, None), (False, 0), (lambda context: context.bs_header.bs_version > 14, None)
		yield 'parallax_max_passes', name_type_map['Float'], (0, None), (False, 4.0), (lambda context: context.bs_header.bs_version > 24, None)
		yield 'parallax_scale', name_type_map['Float'], (0, None), (False, 1.0), (lambda context: context.bs_header.bs_version > 24, None)
		yield 'emissive_color', name_type_map['Color4'], (0, None), (False, None), (lambda context: context.bs_header.bs_version > 34, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'texture_set', name_type_map['Ref'], (0, name_type_map['BSShaderTextureSet']), (False, None)
		if instance.context.bs_header.bs_version > 14:
			yield 'refraction_strength', name_type_map['Float'], (0, None), (False, 0.0)
			yield 'refraction_fire_period', name_type_map['Int'], (0, None), (False, 0)
		if instance.context.bs_header.bs_version > 24:
			yield 'parallax_max_passes', name_type_map['Float'], (0, None), (False, 4.0)
			yield 'parallax_scale', name_type_map['Float'], (0, None), (False, 1.0)
		if instance.context.bs_header.bs_version > 34:
			yield 'emissive_color', name_type_map['Color4'], (0, None), (False, None)

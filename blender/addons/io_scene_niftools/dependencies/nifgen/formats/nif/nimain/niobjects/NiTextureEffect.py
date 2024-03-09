from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nimain.niobjects.NiDynamicEffect import NiDynamicEffect


class NiTextureEffect(NiDynamicEffect):

	"""
	Represents an effect that uses projected textures such as projected lights (gobos), environment maps, and fog maps.
	"""

	__name__ = 'NiTextureEffect'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# Model projection matrix.  Always identity?
		self.model_projection_matrix = name_type_map['Matrix33'](self.context, 0, None)

		# Model projection translation.  Always (0,0,0)?
		self.model_projection_translation = name_type_map['Vector3'](self.context, 0, None)

		# Texture Filtering mode.
		self.texture_filtering = name_type_map['TexFilterMode'].FILTER_TRILERP
		self.max_anisotropy = name_type_map['Ushort'](self.context, 0, None)

		# Texture Clamp mode.
		self.texture_clamping = name_type_map['TexClampMode'].WRAP_S_WRAP_T

		# The type of effect that the texture is used for.
		self.texture_type = name_type_map['TextureType'].TEX_ENVIRONMENT_MAP

		# The method that will be used to generate UV coordinates for the texture effect.
		self.coordinate_generation_type = name_type_map['CoordGenType'].CG_SPHERE_MAP

		# Image index.
		self.image = name_type_map['Ref'](self.context, 0, name_type_map['NiImage'])

		# Source texture index.
		self.source_texture = name_type_map['Ref'](self.context, 0, name_type_map['NiSourceTexture'])

		# Determines whether a clipping plane is used. Always 8-bit.
		self.enable_plane = name_type_map['Byte'].from_value(0)
		self.plane = name_type_map['NiPlane'](self.context, 0, None)
		self.ps_2_l = name_type_map['Short'].from_value(0)
		self.ps_2_k = name_type_map['Short'].from_value(-75)
		self.unknown_short = name_type_map['Ushort'].from_value(0)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'model_projection_matrix', name_type_map['Matrix33'], (0, None), (False, None), (None, None)
		yield 'model_projection_translation', name_type_map['Vector3'], (0, None), (False, None), (None, None)
		yield 'texture_filtering', name_type_map['TexFilterMode'], (0, None), (False, name_type_map['TexFilterMode'].FILTER_TRILERP), (None, None)
		yield 'max_anisotropy', name_type_map['Ushort'], (0, None), (False, None), (lambda context: context.version >= 335872004, None)
		yield 'texture_clamping', name_type_map['TexClampMode'], (0, None), (False, name_type_map['TexClampMode'].WRAP_S_WRAP_T), (None, None)
		yield 'texture_type', name_type_map['TextureType'], (0, None), (False, name_type_map['TextureType'].TEX_ENVIRONMENT_MAP), (None, None)
		yield 'coordinate_generation_type', name_type_map['CoordGenType'], (0, None), (False, name_type_map['CoordGenType'].CG_SPHERE_MAP), (None, None)
		yield 'image', name_type_map['Ref'], (0, name_type_map['NiImage']), (False, None), (lambda context: context.version <= 50397184, None)
		yield 'source_texture', name_type_map['Ref'], (0, name_type_map['NiSourceTexture']), (False, None), (lambda context: context.version >= 50397184, None)
		yield 'enable_plane', name_type_map['Byte'], (0, None), (False, 0), (None, None)
		yield 'plane', name_type_map['NiPlane'], (0, None), (False, None), (None, None)
		yield 'ps_2_l', name_type_map['Short'], (0, None), (False, 0), (lambda context: context.version <= 167903232, None)
		yield 'ps_2_k', name_type_map['Short'], (0, None), (False, -75), (lambda context: context.version <= 167903232, None)
		yield 'unknown_short', name_type_map['Ushort'], (0, None), (False, 0), (lambda context: context.version <= 67174412, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'model_projection_matrix', name_type_map['Matrix33'], (0, None), (False, None)
		yield 'model_projection_translation', name_type_map['Vector3'], (0, None), (False, None)
		yield 'texture_filtering', name_type_map['TexFilterMode'], (0, None), (False, name_type_map['TexFilterMode'].FILTER_TRILERP)
		if instance.context.version >= 335872004:
			yield 'max_anisotropy', name_type_map['Ushort'], (0, None), (False, None)
		yield 'texture_clamping', name_type_map['TexClampMode'], (0, None), (False, name_type_map['TexClampMode'].WRAP_S_WRAP_T)
		yield 'texture_type', name_type_map['TextureType'], (0, None), (False, name_type_map['TextureType'].TEX_ENVIRONMENT_MAP)
		yield 'coordinate_generation_type', name_type_map['CoordGenType'], (0, None), (False, name_type_map['CoordGenType'].CG_SPHERE_MAP)
		if instance.context.version <= 50397184:
			yield 'image', name_type_map['Ref'], (0, name_type_map['NiImage']), (False, None)
		if instance.context.version >= 50397184:
			yield 'source_texture', name_type_map['Ref'], (0, name_type_map['NiSourceTexture']), (False, None)
		yield 'enable_plane', name_type_map['Byte'], (0, None), (False, 0)
		yield 'plane', name_type_map['NiPlane'], (0, None), (False, None)
		if instance.context.version <= 167903232:
			yield 'ps_2_l', name_type_map['Short'], (0, None), (False, 0)
			yield 'ps_2_k', name_type_map['Short'], (0, None), (False, -75)
		if instance.context.version <= 67174412:
			yield 'unknown_short', name_type_map['Ushort'], (0, None), (False, 0)

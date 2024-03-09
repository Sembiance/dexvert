from nifgen.base_struct import BaseStruct
from nifgen.formats.nif.imports import name_type_map


class TexDesc(BaseStruct):

	"""
	NiTexturingProperty::Map. Texture description.
	"""

	__name__ = 'TexDesc'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# Link to the texture image.
		self.image = name_type_map['Ref'](self.context, 0, name_type_map['NiImage'])

		# NiSourceTexture object index.
		self.source = name_type_map['Ref'](self.context, 0, name_type_map['NiSourceTexture'])

		# 0=clamp S clamp T, 1=clamp S wrap T, 2=wrap S clamp T, 3=wrap S wrap T
		self.clamp_mode = name_type_map['TexClampMode'].WRAP_S_WRAP_T

		# 0=nearest, 1=bilinear, 2=trilinear, 3=..., 4=..., 5=...
		self.filter_mode = name_type_map['TexFilterMode'].FILTER_TRILERP

		# Texture mode flags; clamp and filter mode stored in upper byte with 0xYZ00 = clamp mode Y, filter mode Z.
		self.flags = name_type_map['TexturingMapFlags'](self.context, 0, None)
		self.max_anisotropy = name_type_map['Ushort'](self.context, 0, None)

		# The texture coordinate set in NiGeometryData that this texture slot will use.
		self.uv_set = name_type_map['Uint'].from_value(0)

		# L can range from 0 to 3 and are used to specify how fast a texture gets blurry.
		self.ps_2_l = name_type_map['Short'].from_value(0)

		# K is used as an offset into the mipmap levels and can range from -2047 to 2047. Positive values push the mipmap towards being blurry and negative values make the mipmap sharper.
		self.ps_2_k = name_type_map['Short'].from_value(-75)
		self.unknown_short_1 = name_type_map['Ushort'](self.context, 0, None)

		# Whether or not the texture coordinates are transformed.
		self.has_texture_transform = name_type_map['Bool'].from_value(False)

		# The UV translation.
		self.translation = name_type_map['TexCoord'](self.context, 0, None)

		# The UV scale.
		self.scale = name_type_map['TexCoord'].from_value((1.0, 1.0))

		# The W axis rotation in texture space.
		self.rotation = name_type_map['Float'].from_value(0.0)

		# Depending on the source, scaling can occur before or after rotation.
		self.transform_method = name_type_map['TransformMethod'](self.context, 0, None)

		# The origin around which the texture rotates.
		self.center = name_type_map['TexCoord'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'image', name_type_map['Ref'], (0, name_type_map['NiImage']), (False, None), (lambda context: context.version <= 50397184, None)
		yield 'source', name_type_map['Ref'], (0, name_type_map['NiSourceTexture']), (False, None), (lambda context: context.version >= 50528269, None)
		yield 'clamp_mode', name_type_map['TexClampMode'], (0, None), (False, name_type_map['TexClampMode'].WRAP_S_WRAP_T), (lambda context: context.version <= 335544325, None)
		yield 'filter_mode', name_type_map['TexFilterMode'], (0, None), (False, name_type_map['TexFilterMode'].FILTER_TRILERP), (lambda context: context.version <= 335544325, None)
		yield 'flags', name_type_map['TexturingMapFlags'], (0, None), (False, None), (lambda context: context.version >= 335609859, None)
		yield 'max_anisotropy', name_type_map['Ushort'], (0, None), (False, None), (lambda context: context.version >= 335872004, None)
		yield 'uv_set', name_type_map['Uint'], (0, None), (False, 0), (lambda context: context.version <= 335544325, None)
		yield 'ps_2_l', name_type_map['Short'], (0, None), (False, 0), (lambda context: context.version <= 168034305, None)
		yield 'ps_2_k', name_type_map['Short'], (0, None), (False, -75), (lambda context: context.version <= 168034305, None)
		yield 'unknown_short_1', name_type_map['Ushort'], (0, None), (False, None), (lambda context: context.version <= 67174412, None)
		yield 'has_texture_transform', name_type_map['Bool'], (0, None), (False, False), (lambda context: context.version >= 167837696, None)
		yield 'translation', name_type_map['TexCoord'], (0, None), (False, None), (lambda context: context.version >= 167837696, True)
		yield 'scale', name_type_map['TexCoord'], (0, None), (False, (1.0, 1.0)), (lambda context: context.version >= 167837696, True)
		yield 'rotation', name_type_map['Float'], (0, None), (False, 0.0), (lambda context: context.version >= 167837696, True)
		yield 'transform_method', name_type_map['TransformMethod'], (0, None), (False, None), (lambda context: context.version >= 167837696, True)
		yield 'center', name_type_map['TexCoord'], (0, None), (False, None), (lambda context: context.version >= 167837696, True)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		if instance.context.version <= 50397184:
			yield 'image', name_type_map['Ref'], (0, name_type_map['NiImage']), (False, None)
		if instance.context.version >= 50528269:
			yield 'source', name_type_map['Ref'], (0, name_type_map['NiSourceTexture']), (False, None)
		if instance.context.version <= 335544325:
			yield 'clamp_mode', name_type_map['TexClampMode'], (0, None), (False, name_type_map['TexClampMode'].WRAP_S_WRAP_T)
			yield 'filter_mode', name_type_map['TexFilterMode'], (0, None), (False, name_type_map['TexFilterMode'].FILTER_TRILERP)
		if instance.context.version >= 335609859:
			yield 'flags', name_type_map['TexturingMapFlags'], (0, None), (False, None)
		if instance.context.version >= 335872004:
			yield 'max_anisotropy', name_type_map['Ushort'], (0, None), (False, None)
		if instance.context.version <= 335544325:
			yield 'uv_set', name_type_map['Uint'], (0, None), (False, 0)
		if instance.context.version <= 168034305:
			yield 'ps_2_l', name_type_map['Short'], (0, None), (False, 0)
			yield 'ps_2_k', name_type_map['Short'], (0, None), (False, -75)
		if instance.context.version <= 67174412:
			yield 'unknown_short_1', name_type_map['Ushort'], (0, None), (False, None)
		if instance.context.version >= 167837696:
			yield 'has_texture_transform', name_type_map['Bool'], (0, None), (False, False)
		if instance.context.version >= 167837696 and instance.has_texture_transform:
			yield 'translation', name_type_map['TexCoord'], (0, None), (False, None)
			yield 'scale', name_type_map['TexCoord'], (0, None), (False, (1.0, 1.0))
			yield 'rotation', name_type_map['Float'], (0, None), (False, 0.0)
			yield 'transform_method', name_type_map['TransformMethod'], (0, None), (False, None)
			yield 'center', name_type_map['TexCoord'], (0, None), (False, None)

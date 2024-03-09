from nifgen.array import Array
from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nimain.niobjects.NiProperty import NiProperty


class NiTexturingProperty(NiProperty):

	"""
	Describes how a fragment shader should be configured for a given piece of geometry.
	"""

	__name__ = 'NiTexturingProperty'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# Property flags.
		self.flags = name_type_map['TexturingFlags'](self.context, 0, None)

		# Determines how the texture will be applied.  Seems to have special functions in Oblivion.
		self.apply_mode = name_type_map['ApplyMode'].APPLY_MODULATE

		# Number of textures.
		self.texture_count = name_type_map['Uint'].from_value(7)
		self.has_base_texture = name_type_map['Bool'](self.context, 0, None)
		self.base_texture = name_type_map['TexDesc'](self.context, 0, None)
		self.has_dark_texture = name_type_map['Bool'](self.context, 0, None)
		self.dark_texture = name_type_map['TexDesc'](self.context, 0, None)
		self.has_detail_texture = name_type_map['Bool'](self.context, 0, None)
		self.detail_texture = name_type_map['TexDesc'](self.context, 0, None)
		self.has_gloss_texture = name_type_map['Bool'](self.context, 0, None)
		self.gloss_texture = name_type_map['TexDesc'](self.context, 0, None)
		self.has_glow_texture = name_type_map['Bool'](self.context, 0, None)
		self.glow_texture = name_type_map['TexDesc'](self.context, 0, None)
		self.has_bump_map_texture = name_type_map['Bool'](self.context, 0, None)
		self.bump_map_texture = name_type_map['TexDesc'](self.context, 0, None)
		self.bump_map_luma_scale = name_type_map['Float'](self.context, 0, None)
		self.bump_map_luma_offset = name_type_map['Float'](self.context, 0, None)
		self.bump_map_matrix = name_type_map['Matrix22'](self.context, 0, None)
		self.has_normal_texture = name_type_map['Bool'](self.context, 0, None)
		self.normal_texture = name_type_map['TexDesc'](self.context, 0, None)
		self.has_parallax_texture = name_type_map['Bool'](self.context, 0, None)
		self.parallax_texture = name_type_map['TexDesc'](self.context, 0, None)
		self.parallax_offset = name_type_map['Float'](self.context, 0, None)
		self.has_decal_0_texture = name_type_map['Bool'](self.context, 0, None)
		self.decal_0_texture = name_type_map['TexDesc'](self.context, 0, None)
		self.has_decal_1_texture = name_type_map['Bool'](self.context, 0, None)
		self.decal_1_texture = name_type_map['TexDesc'](self.context, 0, None)
		self.has_decal_2_texture = name_type_map['Bool'](self.context, 0, None)
		self.decal_2_texture = name_type_map['TexDesc'](self.context, 0, None)
		self.has_decal_3_texture = name_type_map['Bool'](self.context, 0, None)
		self.decal_3_texture = name_type_map['TexDesc'](self.context, 0, None)
		self.num_shader_textures = name_type_map['Uint'](self.context, 0, None)
		self.shader_textures = Array(self.context, 0, None, (0,), name_type_map['ShaderTexDesc'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'flags', name_type_map['Ushort'], (0, None), (False, None), (lambda context: context.version <= 167772418, None)
		yield 'flags', name_type_map['TexturingFlags'], (0, None), (False, None), (lambda context: context.version >= 335609858, None)
		yield 'apply_mode', name_type_map['ApplyMode'], (0, None), (False, name_type_map['ApplyMode'].APPLY_MODULATE), (lambda context: 50528269 <= context.version <= 335609857, None)
		yield 'texture_count', name_type_map['Uint'], (0, None), (False, 7), (None, None)
		yield 'has_base_texture', name_type_map['Bool'], (0, None), (False, None), (None, True)
		yield 'base_texture', name_type_map['TexDesc'], (0, None), (False, None), (None, True)
		yield 'has_dark_texture', name_type_map['Bool'], (0, None), (False, None), (None, True)
		yield 'dark_texture', name_type_map['TexDesc'], (0, None), (False, None), (None, True)
		yield 'has_detail_texture', name_type_map['Bool'], (0, None), (False, None), (None, True)
		yield 'detail_texture', name_type_map['TexDesc'], (0, None), (False, None), (None, True)
		yield 'has_gloss_texture', name_type_map['Bool'], (0, None), (False, None), (None, True)
		yield 'gloss_texture', name_type_map['TexDesc'], (0, None), (False, None), (None, True)
		yield 'has_glow_texture', name_type_map['Bool'], (0, None), (False, None), (None, True)
		yield 'glow_texture', name_type_map['TexDesc'], (0, None), (False, None), (None, True)
		yield 'has_bump_map_texture', name_type_map['Bool'], (0, None), (False, None), (lambda context: context.version >= 50528269, True)
		yield 'bump_map_texture', name_type_map['TexDesc'], (0, None), (False, None), (lambda context: context.version >= 50528269, True)
		yield 'bump_map_luma_scale', name_type_map['Float'], (0, None), (False, None), (lambda context: context.version >= 50528269, True)
		yield 'bump_map_luma_offset', name_type_map['Float'], (0, None), (False, None), (lambda context: context.version >= 50528269, True)
		yield 'bump_map_matrix', name_type_map['Matrix22'], (0, None), (False, None), (lambda context: context.version >= 50528269, True)
		yield 'has_normal_texture', name_type_map['Bool'], (0, None), (False, None), (lambda context: context.version >= 335675397, True)
		yield 'normal_texture', name_type_map['TexDesc'], (0, None), (False, None), (lambda context: context.version >= 335675397, True)
		yield 'has_parallax_texture', name_type_map['Bool'], (0, None), (False, None), (lambda context: context.version >= 335675397, True)
		yield 'parallax_texture', name_type_map['TexDesc'], (0, None), (False, None), (lambda context: context.version >= 335675397, True)
		yield 'parallax_offset', name_type_map['Float'], (0, None), (False, None), (lambda context: context.version >= 335675397, True)
		yield 'has_decal_0_texture', name_type_map['Bool'], (0, None), (False, None), (lambda context: context.version <= 335675396, True)
		yield 'has_decal_0_texture', name_type_map['Bool'], (0, None), (False, None), (lambda context: context.version >= 335675397, True)
		yield 'decal_0_texture', name_type_map['TexDesc'], (0, None), (False, None), (None, True)
		yield 'has_decal_1_texture', name_type_map['Bool'], (0, None), (False, None), (lambda context: context.version <= 335675396, True)
		yield 'has_decal_1_texture', name_type_map['Bool'], (0, None), (False, None), (lambda context: context.version >= 335675397, True)
		yield 'decal_1_texture', name_type_map['TexDesc'], (0, None), (False, None), (None, True)
		yield 'has_decal_2_texture', name_type_map['Bool'], (0, None), (False, None), (lambda context: context.version <= 335675396, True)
		yield 'has_decal_2_texture', name_type_map['Bool'], (0, None), (False, None), (lambda context: context.version >= 335675397, True)
		yield 'decal_2_texture', name_type_map['TexDesc'], (0, None), (False, None), (None, True)
		yield 'has_decal_3_texture', name_type_map['Bool'], (0, None), (False, None), (lambda context: context.version <= 335675396, True)
		yield 'has_decal_3_texture', name_type_map['Bool'], (0, None), (False, None), (lambda context: context.version >= 335675397, True)
		yield 'decal_3_texture', name_type_map['TexDesc'], (0, None), (False, None), (None, True)
		yield 'num_shader_textures', name_type_map['Uint'], (0, None), (False, None), (lambda context: context.version >= 167772416, None)
		yield 'shader_textures', Array, (0, None, (None,), name_type_map['ShaderTexDesc']), (False, None), (lambda context: context.version >= 167772416, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		if instance.context.version <= 167772418:
			yield 'flags', name_type_map['Ushort'], (0, None), (False, None)
		if instance.context.version >= 335609858:
			yield 'flags', name_type_map['TexturingFlags'], (0, None), (False, None)
		if 50528269 <= instance.context.version <= 335609857:
			yield 'apply_mode', name_type_map['ApplyMode'], (0, None), (False, name_type_map['ApplyMode'].APPLY_MODULATE)
		yield 'texture_count', name_type_map['Uint'], (0, None), (False, 7)
		if instance.texture_count > 0:
			yield 'has_base_texture', name_type_map['Bool'], (0, None), (False, None)
		if instance.has_base_texture:
			yield 'base_texture', name_type_map['TexDesc'], (0, None), (False, None)
		if instance.texture_count > 1:
			yield 'has_dark_texture', name_type_map['Bool'], (0, None), (False, None)
		if instance.has_dark_texture:
			yield 'dark_texture', name_type_map['TexDesc'], (0, None), (False, None)
		if instance.texture_count > 2:
			yield 'has_detail_texture', name_type_map['Bool'], (0, None), (False, None)
		if instance.has_detail_texture:
			yield 'detail_texture', name_type_map['TexDesc'], (0, None), (False, None)
		if instance.texture_count > 3:
			yield 'has_gloss_texture', name_type_map['Bool'], (0, None), (False, None)
		if instance.has_gloss_texture:
			yield 'gloss_texture', name_type_map['TexDesc'], (0, None), (False, None)
		if instance.texture_count > 4:
			yield 'has_glow_texture', name_type_map['Bool'], (0, None), (False, None)
		if instance.has_glow_texture:
			yield 'glow_texture', name_type_map['TexDesc'], (0, None), (False, None)
		if instance.context.version >= 50528269 and instance.texture_count > 5:
			yield 'has_bump_map_texture', name_type_map['Bool'], (0, None), (False, None)
		if instance.context.version >= 50528269 and instance.has_bump_map_texture:
			yield 'bump_map_texture', name_type_map['TexDesc'], (0, None), (False, None)
			yield 'bump_map_luma_scale', name_type_map['Float'], (0, None), (False, None)
			yield 'bump_map_luma_offset', name_type_map['Float'], (0, None), (False, None)
			yield 'bump_map_matrix', name_type_map['Matrix22'], (0, None), (False, None)
		if instance.context.version >= 335675397 and instance.texture_count > 6:
			yield 'has_normal_texture', name_type_map['Bool'], (0, None), (False, None)
		if instance.context.version >= 335675397 and instance.has_normal_texture:
			yield 'normal_texture', name_type_map['TexDesc'], (0, None), (False, None)
		if instance.context.version >= 335675397 and instance.texture_count > 7:
			yield 'has_parallax_texture', name_type_map['Bool'], (0, None), (False, None)
		if instance.context.version >= 335675397 and instance.has_parallax_texture:
			yield 'parallax_texture', name_type_map['TexDesc'], (0, None), (False, None)
			yield 'parallax_offset', name_type_map['Float'], (0, None), (False, None)
		if instance.context.version <= 335675396 and instance.texture_count > 6:
			yield 'has_decal_0_texture', name_type_map['Bool'], (0, None), (False, None)
		if instance.context.version >= 335675397 and instance.texture_count > 8:
			yield 'has_decal_0_texture', name_type_map['Bool'], (0, None), (False, None)
		if instance.has_decal_0_texture:
			yield 'decal_0_texture', name_type_map['TexDesc'], (0, None), (False, None)
		if instance.context.version <= 335675396 and instance.texture_count > 7:
			yield 'has_decal_1_texture', name_type_map['Bool'], (0, None), (False, None)
		if instance.context.version >= 335675397 and instance.texture_count > 9:
			yield 'has_decal_1_texture', name_type_map['Bool'], (0, None), (False, None)
		if instance.has_decal_1_texture:
			yield 'decal_1_texture', name_type_map['TexDesc'], (0, None), (False, None)
		if instance.context.version <= 335675396 and instance.texture_count > 8:
			yield 'has_decal_2_texture', name_type_map['Bool'], (0, None), (False, None)
		if instance.context.version >= 335675397 and instance.texture_count > 10:
			yield 'has_decal_2_texture', name_type_map['Bool'], (0, None), (False, None)
		if instance.has_decal_2_texture:
			yield 'decal_2_texture', name_type_map['TexDesc'], (0, None), (False, None)
		if instance.context.version <= 335675396 and instance.texture_count > 9:
			yield 'has_decal_3_texture', name_type_map['Bool'], (0, None), (False, None)
		if instance.context.version >= 335675397 and instance.texture_count > 11:
			yield 'has_decal_3_texture', name_type_map['Bool'], (0, None), (False, None)
		if instance.has_decal_3_texture:
			yield 'decal_3_texture', name_type_map['TexDesc'], (0, None), (False, None)
		if instance.context.version >= 167772416:
			yield 'num_shader_textures', name_type_map['Uint'], (0, None), (False, None)
			yield 'shader_textures', Array, (0, None, (instance.num_shader_textures,), name_type_map['ShaderTexDesc']), (False, None)

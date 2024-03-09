from nifgen.array import Array
from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nimain.niobjects.NiObject import NiObject


class BSShaderTextureSet(NiObject):

	"""
	Bethesda-specific Texture Set.
	"""

	__name__ = 'BSShaderTextureSet'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.num_textures = name_type_map['Uint'].from_value(6)

		# Textures.
		# 0: Diffuse
		# 1: Normal/Gloss
		# 2: Glow(SLSF2_Glow_Map)/Skin/Hair/Rim light(SLSF2_Rim_Lighting)
		# 3: Height/Parallax
		# 4: Environment
		# 5: Environment Mask
		# 6: Subsurface for Multilayer Parallax
		# 7: Back Lighting Map (SLSF2_Back_Lighting)
		self.textures = Array(self.context, 0, None, (0,), name_type_map['SizedString'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'num_textures', name_type_map['Uint'], (0, None), (False, 6), (None, None)
		yield 'textures', Array, (0, None, (None,), name_type_map['SizedString']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'num_textures', name_type_map['Uint'], (0, None), (False, 6)
		yield 'textures', Array, (0, None, (instance.num_textures,), name_type_map['SizedString']), (False, None)

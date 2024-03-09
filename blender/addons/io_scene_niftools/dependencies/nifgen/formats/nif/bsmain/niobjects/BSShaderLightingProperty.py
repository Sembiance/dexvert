from nifgen.formats.nif.bsmain.niobjects.BSShaderProperty import BSShaderProperty
from nifgen.formats.nif.imports import name_type_map


class BSShaderLightingProperty(BSShaderProperty):

	"""
	Bethesda-specific property.
	"""

	__name__ = 'BSShaderLightingProperty'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# How to handle texture borders.
		self.texture_clamp_mode = name_type_map['TexClampMode'].WRAP_S_WRAP_T
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'texture_clamp_mode', name_type_map['TexClampMode'], (0, None), (False, name_type_map['TexClampMode'].WRAP_S_WRAP_T), (lambda context: context.bs_header.bs_version <= 34, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		if instance.context.bs_header.bs_version <= 34:
			yield 'texture_clamp_mode', name_type_map['TexClampMode'], (0, None), (False, name_type_map['TexClampMode'].WRAP_S_WRAP_T)

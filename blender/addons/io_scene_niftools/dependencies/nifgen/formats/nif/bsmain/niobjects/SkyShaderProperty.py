from nifgen.formats.nif.bsmain.niobjects.BSShaderLightingProperty import BSShaderLightingProperty
from nifgen.formats.nif.imports import name_type_map


class SkyShaderProperty(BSShaderLightingProperty):

	"""
	Bethesda-specific property. Found in Fallout3
	"""

	__name__ = 'SkyShaderProperty'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# The texture.
		self.file_name = name_type_map['SizedString'](self.context, 0, None)

		# Sky Object Type
		self.sky_object_type = name_type_map['SkyObjectType'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'file_name', name_type_map['SizedString'], (0, None), (False, None), (None, None)
		yield 'sky_object_type', name_type_map['SkyObjectType'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'file_name', name_type_map['SizedString'], (0, None), (False, None)
		yield 'sky_object_type', name_type_map['SkyObjectType'], (0, None), (False, None)

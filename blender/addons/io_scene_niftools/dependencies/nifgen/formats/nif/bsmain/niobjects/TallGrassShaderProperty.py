from nifgen.formats.nif.bsmain.niobjects.BSShaderProperty import BSShaderProperty
from nifgen.formats.nif.imports import name_type_map


class TallGrassShaderProperty(BSShaderProperty):

	"""
	Bethesda-specific property.
	"""

	__name__ = 'TallGrassShaderProperty'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# Texture file name
		self.file_name = name_type_map['SizedString'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'file_name', name_type_map['SizedString'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'file_name', name_type_map['SizedString'], (0, None), (False, None)

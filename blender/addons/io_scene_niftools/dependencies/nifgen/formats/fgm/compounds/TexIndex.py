from nifgen.formats.fgm.imports import name_type_map
from nifgen.formats.ovl_base.compounds.MemStruct import MemStruct


class TexIndex(MemStruct):

	"""
	stores index into shader and array index of texture
	"""

	__name__ = 'TexIndex'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self._tex_index = name_type_map['Uint'](self.context, 0, None)

		# index of tile if an array texture is used eg JWE swatches
		self.array_index = name_type_map['Uint'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield '_tex_index', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'array_index', name_type_map['Uint'], (0, None), (False, None), (lambda context: context.version >= 18, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield '_tex_index', name_type_map['Uint'], (0, None), (False, None)
		if instance.context.version >= 18:
			yield 'array_index', name_type_map['Uint'], (0, None), (False, None)

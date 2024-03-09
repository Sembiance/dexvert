from nifgen.array import Array
from nifgen.base_struct import BaseStruct
from nifgen.formats.nif.imports import name_type_map


class BSShaderTextureArray(BaseStruct):

	__name__ = 'BSShaderTextureArray'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.unknown_byte = name_type_map['Byte'].from_value(1)
		self.num_texture_arrays = name_type_map['Uint'](self.context, 0, None)
		self.texture_arrays = Array(self.context, 0, None, (0,), name_type_map['BSTextureArray'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'unknown_byte', name_type_map['Byte'], (0, None), (False, 1), (None, None)
		yield 'num_texture_arrays', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'texture_arrays', Array, (0, None, (None,), name_type_map['BSTextureArray']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'unknown_byte', name_type_map['Byte'], (0, None), (False, 1)
		yield 'num_texture_arrays', name_type_map['Uint'], (0, None), (False, None)
		yield 'texture_arrays', Array, (0, None, (instance.num_texture_arrays,), name_type_map['BSTextureArray']), (False, None)

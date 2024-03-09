from nifgen.array import Array
from nifgen.base_struct import BaseStruct
from nifgen.formats.nif.imports import name_type_map


class BSTextureArray(BaseStruct):

	__name__ = 'BSTextureArray'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.texture_array_width = name_type_map['Uint'](self.context, 0, None)
		self.texture_array = Array(self.context, 0, None, (0,), name_type_map['SizedString'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'texture_array_width', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'texture_array', Array, (0, None, (None,), name_type_map['SizedString']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'texture_array_width', name_type_map['Uint'], (0, None), (False, None)
		yield 'texture_array', Array, (0, None, (instance.texture_array_width,), name_type_map['SizedString']), (False, None)

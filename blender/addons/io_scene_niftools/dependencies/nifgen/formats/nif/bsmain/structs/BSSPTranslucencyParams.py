from nifgen.base_struct import BaseStruct
from nifgen.formats.nif.imports import name_type_map


class BSSPTranslucencyParams(BaseStruct):

	__name__ = 'BSSPTranslucencyParams'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.subsurface_color = name_type_map['Color3'](self.context, 0, None)
		self.transmissive_scale = name_type_map['Float'](self.context, 0, None)
		self.turbulence = name_type_map['Float'](self.context, 0, None)
		self.thick_object = name_type_map['Bool'](self.context, 0, None)
		self.mix_albedo = name_type_map['Bool'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'subsurface_color', name_type_map['Color3'], (0, None), (False, None), (None, None)
		yield 'transmissive_scale', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'turbulence', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'thick_object', name_type_map['Bool'], (0, None), (False, None), (None, None)
		yield 'mix_albedo', name_type_map['Bool'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'subsurface_color', name_type_map['Color3'], (0, None), (False, None)
		yield 'transmissive_scale', name_type_map['Float'], (0, None), (False, None)
		yield 'turbulence', name_type_map['Float'], (0, None), (False, None)
		yield 'thick_object', name_type_map['Bool'], (0, None), (False, None)
		yield 'mix_albedo', name_type_map['Bool'], (0, None), (False, None)

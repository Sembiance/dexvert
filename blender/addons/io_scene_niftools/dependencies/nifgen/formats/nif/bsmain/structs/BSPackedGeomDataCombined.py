from nifgen.base_struct import BaseStruct
from nifgen.formats.nif.imports import name_type_map


class BSPackedGeomDataCombined(BaseStruct):

	__name__ = 'BSPackedGeomDataCombined'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.grayscale_to_palette_scale = name_type_map['Float'](self.context, 0, None)
		self.transform = name_type_map['NiTransform'](self.context, 0, None)
		self.bounding_sphere = name_type_map['NiBound'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'grayscale_to_palette_scale', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'transform', name_type_map['NiTransform'], (0, None), (False, None), (None, None)
		yield 'bounding_sphere', name_type_map['NiBound'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'grayscale_to_palette_scale', name_type_map['Float'], (0, None), (False, None)
		yield 'transform', name_type_map['NiTransform'], (0, None), (False, None)
		yield 'bounding_sphere', name_type_map['NiBound'], (0, None), (False, None)

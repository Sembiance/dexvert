from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nianimation.niobjects.NiBSplineEvaluator import NiBSplineEvaluator


class NiBSplineTransformEvaluator(NiBSplineEvaluator):

	__name__ = 'NiBSplineTransformEvaluator'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.transform = name_type_map['NiQuatTransform'](self.context, 0, None)

		# Handle into the translation data. (USHRT_MAX for invalid handle.)
		self.translation_handle = name_type_map['Uint'].from_value(65535)

		# Handle into the rotation data. (USHRT_MAX for invalid handle.)
		self.rotation_handle = name_type_map['Uint'].from_value(65535)

		# Handle into the scale data. (USHRT_MAX for invalid handle.)
		self.scale_handle = name_type_map['Uint'].from_value(65535)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'transform', name_type_map['NiQuatTransform'], (0, None), (False, None), (None, None)
		yield 'translation_handle', name_type_map['Uint'], (0, None), (False, 65535), (None, None)
		yield 'rotation_handle', name_type_map['Uint'], (0, None), (False, 65535), (None, None)
		yield 'scale_handle', name_type_map['Uint'], (0, None), (False, 65535), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'transform', name_type_map['NiQuatTransform'], (0, None), (False, None)
		yield 'translation_handle', name_type_map['Uint'], (0, None), (False, 65535)
		yield 'rotation_handle', name_type_map['Uint'], (0, None), (False, 65535)
		yield 'scale_handle', name_type_map['Uint'], (0, None), (False, 65535)

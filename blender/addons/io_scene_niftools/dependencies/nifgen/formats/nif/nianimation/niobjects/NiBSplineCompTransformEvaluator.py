from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nianimation.niobjects.NiBSplineTransformEvaluator import NiBSplineTransformEvaluator


class NiBSplineCompTransformEvaluator(NiBSplineTransformEvaluator):

	__name__ = 'NiBSplineCompTransformEvaluator'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.translation_offset = name_type_map['Float'].from_value(3.402823466e+38)
		self.translation_half_range = name_type_map['Float'].from_value(3.402823466e+38)
		self.rotation_offset = name_type_map['Float'].from_value(3.402823466e+38)
		self.rotation_half_range = name_type_map['Float'].from_value(3.402823466e+38)
		self.scale_offset = name_type_map['Float'].from_value(3.402823466e+38)
		self.scale_half_range = name_type_map['Float'].from_value(3.402823466e+38)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'translation_offset', name_type_map['Float'], (0, None), (False, 3.402823466e+38), (None, None)
		yield 'translation_half_range', name_type_map['Float'], (0, None), (False, 3.402823466e+38), (None, None)
		yield 'rotation_offset', name_type_map['Float'], (0, None), (False, 3.402823466e+38), (None, None)
		yield 'rotation_half_range', name_type_map['Float'], (0, None), (False, 3.402823466e+38), (None, None)
		yield 'scale_offset', name_type_map['Float'], (0, None), (False, 3.402823466e+38), (None, None)
		yield 'scale_half_range', name_type_map['Float'], (0, None), (False, 3.402823466e+38), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'translation_offset', name_type_map['Float'], (0, None), (False, 3.402823466e+38)
		yield 'translation_half_range', name_type_map['Float'], (0, None), (False, 3.402823466e+38)
		yield 'rotation_offset', name_type_map['Float'], (0, None), (False, 3.402823466e+38)
		yield 'rotation_half_range', name_type_map['Float'], (0, None), (False, 3.402823466e+38)
		yield 'scale_offset', name_type_map['Float'], (0, None), (False, 3.402823466e+38)
		yield 'scale_half_range', name_type_map['Float'], (0, None), (False, 3.402823466e+38)

from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nianimation.niobjects.NiBSplineTransformInterpolator import NiBSplineTransformInterpolator


class NiBSplineCompTransformInterpolator(NiBSplineTransformInterpolator):

	"""
	NiBSplineTransformInterpolator plus the information required for using compact control points.
	"""

	__name__ = 'NiBSplineCompTransformInterpolator'


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

	def get_translations(self):
		"""Return an iterator over all translation keys."""
		return self._getCompKeys(self.translation_handle, 3,
								 self.translation_offset, self.translation_half_range)

	def get_rotations(self):
		"""Return an iterator over all rotation keys."""
		return self._getCompKeys(self.rotation_handle, 4,
								 self.rotation_offset, self.rotation_half_range)

	def get_scales(self):
		"""Return an iterator over all scale keys."""
		for key in self._getCompKeys(self.scale_handle, 1,
									 self.scale_offset, self.scale_half_range):
			yield key[0]

	def apply_scale(self, scale):
		"""Apply scale factor on data."""
		super().apply_scale(scale)
		self.translation_offset *= scale
		self.translation_half_range *= scale


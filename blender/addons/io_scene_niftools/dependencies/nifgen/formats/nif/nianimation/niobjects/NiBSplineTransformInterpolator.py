from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nianimation.niobjects.NiBSplineInterpolator import NiBSplineInterpolator


class NiBSplineTransformInterpolator(NiBSplineInterpolator):

	"""
	Supports the animation of position, rotation, and scale using an NiQuatTransform.
	The NiQuatTransform can be an unchanging pose or interpolated from B-Spline control point channels.
	"""

	__name__ = 'NiBSplineTransformInterpolator'


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
	def get_translations(self):
		"""Return an iterator over all translation keys."""
		return self._getFloatKeys(self.translation_handle, 3)

	def get_rotations(self):
		"""Return an iterator over all rotation keys."""
		return self._getFloatKeys(self.rotation_handle, 4)

	def get_scales(self):
		"""Return an iterator over all scale keys."""
		for key in self._getFloatKeys(self.scale_handle, 1):
			yield key[0]

	def apply_scale(self, scale):
		"""Apply scale factor on data."""
		super().apply_scale(scale)
		self.transform.apply_scale(scale)
		# also scale translation float keys
		if self.translation_handle != 65535:
			offset = self.translation_handle
			num_elements = self.basis_data.num_control_points
			element_size = 3
			controlpoints = self.spline_data.float_control_points
			if len(controlpoints) > 0:
				for element in range(num_elements):
					for index in range(element_size):
						controlpoints[offset + element * element_size + index] *= scale


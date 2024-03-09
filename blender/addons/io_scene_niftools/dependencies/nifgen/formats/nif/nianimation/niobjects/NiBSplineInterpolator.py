from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nianimation.niobjects.NiInterpolator import NiInterpolator


class NiBSplineInterpolator(NiInterpolator):

	"""
	Abstract base class for interpolators storing data via a B-spline.
	"""

	__name__ = 'NiBSplineInterpolator'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# Animation start time.
		self.start_time = name_type_map['Float'].from_value(3.402823466e+38)

		# Animation stop time.
		self.stop_time = name_type_map['Float'].from_value(-3.402823466e+38)
		self.spline_data = name_type_map['Ref'](self.context, 0, name_type_map['NiBSplineData'])
		self.basis_data = name_type_map['Ref'](self.context, 0, name_type_map['NiBSplineBasisData'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'start_time', name_type_map['Float'], (0, None), (False, 3.402823466e+38), (None, None)
		yield 'stop_time', name_type_map['Float'], (0, None), (False, -3.402823466e+38), (None, None)
		yield 'spline_data', name_type_map['Ref'], (0, name_type_map['NiBSplineData']), (False, None), (None, None)
		yield 'basis_data', name_type_map['Ref'], (0, name_type_map['NiBSplineBasisData']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'start_time', name_type_map['Float'], (0, None), (False, 3.402823466e+38)
		yield 'stop_time', name_type_map['Float'], (0, None), (False, -3.402823466e+38)
		yield 'spline_data', name_type_map['Ref'], (0, name_type_map['NiBSplineData']), (False, None)
		yield 'basis_data', name_type_map['Ref'], (0, name_type_map['NiBSplineBasisData']), (False, None)
	def get_times(self):
		"""Return an iterator over all key times.

		@todo: When code for calculating the bsplines is ready, this function
		will return exactly self.basis_data.num_control_points - 1 time points, and
		not self.basis_data.num_control_points as it is now.
		"""
		# is there basis data?
		if not self.basis_data:
			return
		# return all times
		for i in range(self.basis_data.num_control_points):
			yield (
				self.start_time
				+ (i * (self.stop_time - self.start_time)
				   / (self.basis_data.num_control_points - 1))
				)

	def _getFloatKeys(self, offset, element_size):
		"""Helper function to get iterator to various keys. Internal use only."""
		# are there keys?
		if offset == 65535:
			return
		# is there basis data and spline data?
		if not self.basis_data or not self.spline_data:
			return
		# yield all keys
		for key in self.spline_data.get_float_data(offset,
												self.basis_data.num_control_points,
												element_size):
			yield key

	def _getCompKeys(self, offset, element_size, bias, multiplier):
		"""Helper function to get iterator to various keys. Internal use only."""
		# are there keys?
		if offset == 65535:
			return
		# is there basis data and spline data?
		if not self.basis_data or not self.spline_data:
			return
		# yield all keys
		for key in self.spline_data.get_comp_data(offset,
											   self.basis_data.num_control_points,
											   element_size,
											   bias, multiplier):
			yield key


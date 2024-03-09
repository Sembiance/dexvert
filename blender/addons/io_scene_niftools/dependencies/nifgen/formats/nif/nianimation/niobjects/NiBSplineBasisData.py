from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nimain.niobjects.NiObject import NiObject


class NiBSplineBasisData(NiObject):

	"""
	Contains an NiBSplineBasis for use in interpolation of open, uniform B-Splines.
	"""

	__name__ = 'NiBSplineBasisData'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# The number of control points of the B-spline (number of frames of animation plus degree of B-spline minus one).
		self.num_control_points = name_type_map['Uint'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'num_control_points', name_type_map['Uint'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'num_control_points', name_type_map['Uint'], (0, None), (False, None)

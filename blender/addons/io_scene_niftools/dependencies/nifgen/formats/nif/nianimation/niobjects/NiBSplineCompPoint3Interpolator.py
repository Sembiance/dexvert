from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nianimation.niobjects.NiBSplinePoint3Interpolator import NiBSplinePoint3Interpolator


class NiBSplineCompPoint3Interpolator(NiBSplinePoint3Interpolator):

	"""
	NiBSplinePoint3Interpolator plus the information required for using compact control points.
	"""

	__name__ = 'NiBSplineCompPoint3Interpolator'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.position_offset = name_type_map['Float'].from_value(3.402823466e+38)
		self.position_half_range = name_type_map['Float'].from_value(3.402823466e+38)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'position_offset', name_type_map['Float'], (0, None), (False, 3.402823466e+38), (None, None)
		yield 'position_half_range', name_type_map['Float'], (0, None), (False, 3.402823466e+38), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'position_offset', name_type_map['Float'], (0, None), (False, 3.402823466e+38)
		yield 'position_half_range', name_type_map['Float'], (0, None), (False, 3.402823466e+38)

from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nianimation.niobjects.NiBSplineInterpolator import NiBSplineInterpolator


class NiBSplinePoint3Interpolator(NiBSplineInterpolator):

	"""
	Uses B-Splines to animate an NiPoint3 value over time.
	"""

	__name__ = 'NiBSplinePoint3Interpolator'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# Base value when curve not defined.
		self.value = name_type_map['Vector3'].from_value((-3.402823466e+38, -3.402823466e+38, -3.402823466e+38))

		# Handle into the data. (USHRT_MAX for invalid handle.)
		self.handle = name_type_map['Uint'].from_value(65535)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'value', name_type_map['Vector3'], (0, None), (False, (-3.402823466e+38, -3.402823466e+38, -3.402823466e+38)), (None, None)
		yield 'handle', name_type_map['Uint'], (0, None), (False, 65535), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'value', name_type_map['Vector3'], (0, None), (False, (-3.402823466e+38, -3.402823466e+38, -3.402823466e+38))
		yield 'handle', name_type_map['Uint'], (0, None), (False, 65535)

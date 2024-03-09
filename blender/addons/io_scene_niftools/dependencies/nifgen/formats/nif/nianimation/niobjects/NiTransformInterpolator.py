from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nianimation.niobjects.NiKeyBasedInterpolator import NiKeyBasedInterpolator


class NiTransformInterpolator(NiKeyBasedInterpolator):

	"""
	An interpolator for transform keyframes.
	"""

	__name__ = 'NiTransformInterpolator'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.transform = name_type_map['NiQuatTransform'](self.context, 0, None)
		self.data = name_type_map['Ref'](self.context, 0, name_type_map['NiTransformData'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'transform', name_type_map['NiQuatTransform'], (0, None), (False, None), (None, None)
		yield 'data', name_type_map['Ref'], (0, name_type_map['NiTransformData']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'transform', name_type_map['NiQuatTransform'], (0, None), (False, None)
		yield 'data', name_type_map['Ref'], (0, name_type_map['NiTransformData']), (False, None)

	def apply_scale(self, scale):
		"""Apply scale factor <scale> on data."""
		super().apply_scale(scale)
		# apply scale on translation
		self.transform.apply_scale(scale)


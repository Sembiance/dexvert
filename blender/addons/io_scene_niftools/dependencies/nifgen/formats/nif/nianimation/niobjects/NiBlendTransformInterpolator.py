from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nianimation.niobjects.NiBlendInterpolator import NiBlendInterpolator


class NiBlendTransformInterpolator(NiBlendInterpolator):

	"""
	Blends NiQuatTransform values together.
	"""

	__name__ = 'NiBlendTransformInterpolator'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.value = name_type_map['NiQuatTransform'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'value', name_type_map['NiQuatTransform'], (0, None), (False, None), (lambda context: context.version <= 167837805, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		if instance.context.version <= 167837805:
			yield 'value', name_type_map['NiQuatTransform'], (0, None), (False, None)

	def apply_scale(self, scale):
		"""Apply scale factor <scale> on data."""
		super().apply_scale(scale)
		self.value.apply_scale(scale)

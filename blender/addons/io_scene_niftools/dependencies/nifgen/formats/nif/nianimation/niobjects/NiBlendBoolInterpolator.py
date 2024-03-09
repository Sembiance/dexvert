from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nianimation.niobjects.NiBlendInterpolator import NiBlendInterpolator


class NiBlendBoolInterpolator(NiBlendInterpolator):

	"""
	Blends bool values together.
	"""

	__name__ = 'NiBlendBoolInterpolator'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# The pose value. Invalid if using data.
		self.value = name_type_map['Byte'].from_value(2)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'value', name_type_map['Byte'], (0, None), (False, 2), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'value', name_type_map['Byte'], (0, None), (False, 2)

from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nianimation.niobjects.NiInterpController import NiInterpController


class NiSingleInterpController(NiInterpController):

	"""
	Uses a single NiInterpolator to animate its target value.
	"""

	__name__ = 'NiSingleInterpController'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.interpolator = name_type_map['Ref'](self.context, 0, name_type_map['NiInterpolator'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'interpolator', name_type_map['Ref'], (0, name_type_map['NiInterpolator']), (False, None), (lambda context: context.version >= 167837800, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		if instance.context.version >= 167837800:
			yield 'interpolator', name_type_map['Ref'], (0, name_type_map['NiInterpolator']), (False, None)

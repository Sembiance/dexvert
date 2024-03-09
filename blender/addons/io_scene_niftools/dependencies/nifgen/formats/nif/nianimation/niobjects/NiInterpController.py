from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nimain.niobjects.NiTimeController import NiTimeController


class NiInterpController(NiTimeController):

	"""
	Abstract base class for all NiTimeController objects using NiInterpolator objects to animate their target objects.
	"""

	__name__ = 'NiInterpController'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.manager_controlled = name_type_map['Bool'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'manager_controlled', name_type_map['Bool'], (0, None), (False, None), (lambda context: 167837800 <= context.version <= 167837804, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		if 167837800 <= instance.context.version <= 167837804:
			yield 'manager_controlled', name_type_map['Bool'], (0, None), (False, None)

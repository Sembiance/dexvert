from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nianimation.niobjects.NiSingleInterpController import NiSingleInterpController


class NiExtraDataController(NiSingleInterpController):

	"""
	Abstract base class for all extra data controllers.
	NiInterpController::GetCtlrID() string format:
	'%s'
	Where %s = Value of "Extra Data Name"
	"""

	__name__ = 'NiExtraDataController'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.extra_data_name = name_type_map['String'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'extra_data_name', name_type_map['String'], (0, None), (False, None), (lambda context: context.version >= 167903232, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		if instance.context.version >= 167903232:
			yield 'extra_data_name', name_type_map['String'], (0, None), (False, None)

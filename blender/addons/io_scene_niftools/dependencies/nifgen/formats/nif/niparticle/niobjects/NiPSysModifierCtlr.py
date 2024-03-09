from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nianimation.niobjects.NiSingleInterpController import NiSingleInterpController


class NiPSysModifierCtlr(NiSingleInterpController):

	"""
	A particle system modifier controller.
	NiInterpController::GetCtlrID() string format:
	'%s'
	Where %s = Value of "Modifier Name"
	"""

	__name__ = 'NiPSysModifierCtlr'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# Used to find the modifier pointer.
		self.modifier_name = name_type_map['String'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'modifier_name', name_type_map['String'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'modifier_name', name_type_map['String'], (0, None), (False, None)

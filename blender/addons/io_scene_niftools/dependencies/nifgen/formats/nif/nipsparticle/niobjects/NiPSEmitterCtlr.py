from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nianimation.niobjects.NiSingleInterpController import NiSingleInterpController


class NiPSEmitterCtlr(NiSingleInterpController):

	"""
	Abstract base class for all particle emitter time controllers.
	"""

	__name__ = 'NiPSEmitterCtlr'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.emitter_name = name_type_map['NiFixedString'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'emitter_name', name_type_map['NiFixedString'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'emitter_name', name_type_map['NiFixedString'], (0, None), (False, None)

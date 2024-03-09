from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.niparticle.niobjects.NiPSysModifierCtlr import NiPSysModifierCtlr


class NiPSysModifierFloatCtlr(NiPSysModifierCtlr):

	"""
	A particle system modifier controller that animates a floating point value for particles.
	"""

	__name__ = 'NiPSysModifierFloatCtlr'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.data = name_type_map['Ref'](self.context, 0, name_type_map['NiFloatData'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'data', name_type_map['Ref'], (0, name_type_map['NiFloatData']), (False, None), (lambda context: context.version <= 167837799, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		if instance.context.version <= 167837799:
			yield 'data', name_type_map['Ref'], (0, name_type_map['NiFloatData']), (False, None)

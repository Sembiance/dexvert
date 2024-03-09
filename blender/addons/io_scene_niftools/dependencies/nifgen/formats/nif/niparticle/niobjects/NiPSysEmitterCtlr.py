from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.niparticle.niobjects.NiPSysModifierCtlr import NiPSysModifierCtlr


class NiPSysEmitterCtlr(NiPSysModifierCtlr):

	"""
	Particle system emitter controller.
	NiInterpController::GetInterpolatorID() string format:
	['BirthRate', 'EmitterActive'] (for "Interpolator" and "Visibility Interpolator" respectively)
	"""

	__name__ = 'NiPSysEmitterCtlr'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.data = name_type_map['Ref'](self.context, 0, name_type_map['NiPSysEmitterCtlrData'])
		self.visibility_interpolator = name_type_map['Ref'](self.context, 0, name_type_map['NiInterpolator'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'data', name_type_map['Ref'], (0, name_type_map['NiPSysEmitterCtlrData']), (False, None), (lambda context: context.version <= 167837799, None)
		yield 'visibility_interpolator', name_type_map['Ref'], (0, name_type_map['NiInterpolator']), (False, None), (lambda context: context.version >= 167837800, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		if instance.context.version <= 167837799:
			yield 'data', name_type_map['Ref'], (0, name_type_map['NiPSysEmitterCtlrData']), (False, None)
		if instance.context.version >= 167837800:
			yield 'visibility_interpolator', name_type_map['Ref'], (0, name_type_map['NiInterpolator']), (False, None)

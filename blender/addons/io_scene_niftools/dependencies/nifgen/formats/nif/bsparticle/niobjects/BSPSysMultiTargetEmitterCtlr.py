from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.niparticle.niobjects.NiPSysEmitterCtlr import NiPSysEmitterCtlr


class BSPSysMultiTargetEmitterCtlr(NiPSysEmitterCtlr):

	"""
	Particle system (multi?) emitter controller.
	"""

	__name__ = 'BSPSysMultiTargetEmitterCtlr'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.max_emitters = name_type_map['Ushort'](self.context, 0, None)
		self.master_particle_system = name_type_map['Ptr'](self.context, 0, name_type_map['BSMasterParticleSystem'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'max_emitters', name_type_map['Ushort'], (0, None), (False, None), (None, None)
		yield 'master_particle_system', name_type_map['Ptr'], (0, name_type_map['BSMasterParticleSystem']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'max_emitters', name_type_map['Ushort'], (0, None), (False, None)
		yield 'master_particle_system', name_type_map['Ptr'], (0, name_type_map['BSMasterParticleSystem']), (False, None)

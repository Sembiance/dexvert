from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nipsparticle.niobjects.NiPSParticleSystem import NiPSParticleSystem


class NiPhysXPSParticleSystem(NiPSParticleSystem):

	"""
	Implements Gamebryo particle systems that use PhysX actors for the particles
	"""

	__name__ = 'NiPhysXPSParticleSystem'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.prop = name_type_map['Ptr'](self.context, 0, name_type_map['NiPhysXPSParticleSystemProp'])
		self.dest = name_type_map['Ptr'](self.context, 0, name_type_map['NiPhysXPSParticleSystemDest'])
		self.scene = name_type_map['Ptr'](self.context, 0, name_type_map['NiPhysXScene'])
		self.phys_x_flags = name_type_map['Byte'](self.context, 0, None)
		self.default_actor_pool_size = name_type_map['Uint'](self.context, 0, None)
		self.generation_pool_size = name_type_map['Uint'](self.context, 0, None)
		self.actor_pool_center = name_type_map['Vector3'](self.context, 0, None)
		self.actor_pool_dimensions = name_type_map['Vector3'](self.context, 0, None)
		self.actor = name_type_map['Ptr'](self.context, 0, name_type_map['NiPhysXActorDesc'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'prop', name_type_map['Ptr'], (0, name_type_map['NiPhysXPSParticleSystemProp']), (False, None), (None, None)
		yield 'dest', name_type_map['Ptr'], (0, name_type_map['NiPhysXPSParticleSystemDest']), (False, None), (None, None)
		yield 'scene', name_type_map['Ptr'], (0, name_type_map['NiPhysXScene']), (False, None), (None, None)
		yield 'phys_x_flags', name_type_map['Byte'], (0, None), (False, None), (None, None)
		yield 'default_actor_pool_size', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'generation_pool_size', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'actor_pool_center', name_type_map['Vector3'], (0, None), (False, None), (None, None)
		yield 'actor_pool_dimensions', name_type_map['Vector3'], (0, None), (False, None), (None, None)
		yield 'actor', name_type_map['Ptr'], (0, name_type_map['NiPhysXActorDesc']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'prop', name_type_map['Ptr'], (0, name_type_map['NiPhysXPSParticleSystemProp']), (False, None)
		yield 'dest', name_type_map['Ptr'], (0, name_type_map['NiPhysXPSParticleSystemDest']), (False, None)
		yield 'scene', name_type_map['Ptr'], (0, name_type_map['NiPhysXScene']), (False, None)
		yield 'phys_x_flags', name_type_map['Byte'], (0, None), (False, None)
		yield 'default_actor_pool_size', name_type_map['Uint'], (0, None), (False, None)
		yield 'generation_pool_size', name_type_map['Uint'], (0, None), (False, None)
		yield 'actor_pool_center', name_type_map['Vector3'], (0, None), (False, None)
		yield 'actor_pool_dimensions', name_type_map['Vector3'], (0, None), (False, None)
		yield 'actor', name_type_map['Ptr'], (0, name_type_map['NiPhysXActorDesc']), (False, None)

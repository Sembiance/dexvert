from nifgen.array import Array
from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nipsparticle.niobjects.NiPSParticleSystem import NiPSParticleSystem


class NiPSMeshParticleSystem(NiPSParticleSystem):

	"""
	Represents a particle system that uses mesh particles instead of sprite-based particles.
	"""

	__name__ = 'NiPSMeshParticleSystem'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.num_generations = name_type_map['Uint'](self.context, 0, None)
		self.master_particles = Array(self.context, 0, name_type_map['NiAVObject'], (0,), name_type_map['Ref'])
		self.pool_size = name_type_map['Uint'](self.context, 0, None)
		self.auto_fill_pools = name_type_map['Bool'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'num_generations', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'master_particles', Array, (0, name_type_map['NiAVObject'], (None,), name_type_map['Ref']), (False, None), (None, None)
		yield 'pool_size', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'auto_fill_pools', name_type_map['Bool'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'num_generations', name_type_map['Uint'], (0, None), (False, None)
		yield 'master_particles', Array, (0, name_type_map['NiAVObject'], (instance.num_generations,), name_type_map['Ref']), (False, None)
		yield 'pool_size', name_type_map['Uint'], (0, None), (False, None)
		yield 'auto_fill_pools', name_type_map['Bool'], (0, None), (False, None)

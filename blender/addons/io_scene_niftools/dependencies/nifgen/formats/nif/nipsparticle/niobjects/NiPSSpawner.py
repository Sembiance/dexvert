from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nimain.niobjects.NiObject import NiObject


class NiPSSpawner(NiObject):

	"""
	Creates a new particle whose initial parameters are based on an existing particle.
	"""

	__name__ = 'NiPSSpawner'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.master_particle_system = name_type_map['Ptr'](self.context, 0, name_type_map['NiPSParticleSystem'])
		self.percentage_spawned = name_type_map['Float'].from_value(1.0)
		self.spawn_speed_factor = name_type_map['Float'].from_value(1.0)
		self.spawn_speed_factor_var = name_type_map['Float'](self.context, 0, None)
		self.spawn_dir_chaos = name_type_map['Float'](self.context, 0, None)
		self.life_span = name_type_map['Float'](self.context, 0, None)
		self.life_span_var = name_type_map['Float'](self.context, 0, None)
		self.num_spawn_generations = name_type_map['Ushort'].from_value(1)
		self.min_to_spawn = name_type_map['Uint'].from_value(1)
		self.max_to_spawn = name_type_map['Uint'].from_value(1)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'master_particle_system', name_type_map['Ptr'], (0, name_type_map['NiPSParticleSystem']), (False, None), (lambda context: context.version >= 335937792, None)
		yield 'percentage_spawned', name_type_map['Float'], (0, None), (False, 1.0), (None, None)
		yield 'spawn_speed_factor', name_type_map['Float'], (0, None), (False, 1.0), (lambda context: context.version >= 335937792, None)
		yield 'spawn_speed_factor_var', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'spawn_dir_chaos', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'life_span', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'life_span_var', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'num_spawn_generations', name_type_map['Ushort'], (0, None), (False, 1), (None, None)
		yield 'min_to_spawn', name_type_map['Uint'], (0, None), (False, 1), (None, None)
		yield 'max_to_spawn', name_type_map['Uint'], (0, None), (False, 1), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		if instance.context.version >= 335937792:
			yield 'master_particle_system', name_type_map['Ptr'], (0, name_type_map['NiPSParticleSystem']), (False, None)
		yield 'percentage_spawned', name_type_map['Float'], (0, None), (False, 1.0)
		if instance.context.version >= 335937792:
			yield 'spawn_speed_factor', name_type_map['Float'], (0, None), (False, 1.0)
		yield 'spawn_speed_factor_var', name_type_map['Float'], (0, None), (False, None)
		yield 'spawn_dir_chaos', name_type_map['Float'], (0, None), (False, None)
		yield 'life_span', name_type_map['Float'], (0, None), (False, None)
		yield 'life_span_var', name_type_map['Float'], (0, None), (False, None)
		yield 'num_spawn_generations', name_type_map['Ushort'], (0, None), (False, 1)
		yield 'min_to_spawn', name_type_map['Uint'], (0, None), (False, 1)
		yield 'max_to_spawn', name_type_map['Uint'], (0, None), (False, 1)

from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.niparticle.niobjects.NiPSysModifier import NiPSysModifier


class NiPSysSpawnModifier(NiPSysModifier):

	"""
	Particle modifier that spawns additional copies of a particle.
	"""

	__name__ = 'NiPSysSpawnModifier'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# Number of allowed generations for spawning. Particles whose generations are >= will not be spawned.
		self.num_spawn_generations = name_type_map['Ushort'].from_value(0)

		# The likelihood of a particular particle being spawned. Must be between 0.0 and 1.0.
		self.percentage_spawned = name_type_map['Float'].from_value(1.0)

		# The minimum particles to spawn for any given original particle.
		self.min_num_to_spawn = name_type_map['Ushort'].from_value(1)

		# The maximum particles to spawn for any given original particle.
		self.max_num_to_spawn = name_type_map['Ushort'].from_value(1)

		# How much the spawned particle speed can vary.
		self.spawn_speed_variation = name_type_map['Float'](self.context, 0, None)

		# How much the spawned particle direction can vary.
		self.spawn_dir_variation = name_type_map['Float'](self.context, 0, None)

		# Lifespan assigned to spawned particles.
		self.life_span = name_type_map['Float'](self.context, 0, None)

		# The amount the lifespan can vary.
		self.life_span_variation = name_type_map['Float'](self.context, 0, None)
		self.world_shift_spawn_speed_addition = name_type_map['Float'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'num_spawn_generations', name_type_map['Ushort'], (0, None), (False, 0), (None, None)
		yield 'percentage_spawned', name_type_map['Float'], (0, None), (False, 1.0), (None, None)
		yield 'min_num_to_spawn', name_type_map['Ushort'], (0, None), (False, 1), (None, None)
		yield 'max_num_to_spawn', name_type_map['Ushort'], (0, None), (False, 1), (None, None)
		yield 'spawn_speed_variation', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'spawn_dir_variation', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'life_span', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'life_span_variation', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'world_shift_spawn_speed_addition', name_type_map['Float'], (0, None), (False, None), (lambda context: 167903233 <= context.version <= 168034305, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'num_spawn_generations', name_type_map['Ushort'], (0, None), (False, 0)
		yield 'percentage_spawned', name_type_map['Float'], (0, None), (False, 1.0)
		yield 'min_num_to_spawn', name_type_map['Ushort'], (0, None), (False, 1)
		yield 'max_num_to_spawn', name_type_map['Ushort'], (0, None), (False, 1)
		yield 'spawn_speed_variation', name_type_map['Float'], (0, None), (False, None)
		yield 'spawn_dir_variation', name_type_map['Float'], (0, None), (False, None)
		yield 'life_span', name_type_map['Float'], (0, None), (False, None)
		yield 'life_span_variation', name_type_map['Float'], (0, None), (False, None)
		if 167903233 <= instance.context.version <= 168034305:
			yield 'world_shift_spawn_speed_addition', name_type_map['Float'], (0, None), (False, None)

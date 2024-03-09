from nifgen.array import Array
from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nimain.niobjects.NiTimeController import NiTimeController


class NiParticleSystemController(NiTimeController):

	"""
	A generic particle system time controller object.
	"""

	__name__ = 'NiParticleSystemController'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# Particle speed in old files
		self.old_speed = name_type_map['Uint'](self.context, 0, None)

		# Particle speed
		self.speed = name_type_map['Float'](self.context, 0, None)

		# Particle random speed modifier
		self.speed_variation = name_type_map['Float'](self.context, 0, None)

		# vertical emit direction [radians]
		# 0.0 : up
		# 1.6 : horizontal
		# 3.1416 : down
		self.declination = name_type_map['Float'](self.context, 0, None)

		# emitter's vertical opening angle [radians]
		self.declination_variation = name_type_map['Float'](self.context, 0, None)

		# horizontal emit direction
		self.planar_angle = name_type_map['Float'](self.context, 0, None)

		# emitter's horizontal opening angle
		self.planar_angle_variation = name_type_map['Float'](self.context, 0, None)
		self.initial_normal = name_type_map['Vector3'].from_value((1.0, 0.0, 0.0))
		self.initial_color = name_type_map['Color4'].from_value((1.0, 1.0, 1.0, 1.0))

		# Particle size
		self.initial_size = name_type_map['Float'].from_value(1.0)

		# Particle emit start time
		self.emit_start_time = name_type_map['Float'](self.context, 0, None)

		# Particle emit stop time
		self.emit_stop_time = name_type_map['Float'](self.context, 0, None)
		self.reset_particle_system = name_type_map['Byte'](self.context, 0, None)

		# Particle emission rate in old files
		self.old_emit_rate = name_type_map['Uint'](self.context, 0, None)

		# Particle emission rate (particles per second)
		self.birth_rate = name_type_map['Float'](self.context, 0, None)

		# Particle lifetime
		self.lifetime = name_type_map['Float'](self.context, 0, None)

		# Particle lifetime random modifier
		self.lifetime_variation = name_type_map['Float'](self.context, 0, None)
		self.use_birth_rate = name_type_map['Byte'](self.context, 0, None)
		self.spawn_on_death = name_type_map['Byte'](self.context, 0, None)
		self.emitter_dimensions = name_type_map['Vector3'](self.context, 0, None)

		# The object which acts as the basis for the particle emitter.
		self.emitter = name_type_map['Ptr'](self.context, 0, name_type_map['NiAVObject'])
		self.num_spawn_generations = name_type_map['Ushort'].from_value(1)
		self.percentage_spawned = name_type_map['Float'].from_value(1.0)
		self.spawn_multiplier = name_type_map['Ushort'](self.context, 0, None)
		self.spawn_speed_chaos = name_type_map['Float'](self.context, 0, None)
		self.spawn_dir_chaos = name_type_map['Float'](self.context, 0, None)

		# Particle velocity
		self.particle_velocity = name_type_map['Vector3'](self.context, 0, None)
		self.particle_unknown_vector = name_type_map['Vector3'](self.context, 0, None)

		# The particle's age.
		self.particle_lifetime = name_type_map['Float'](self.context, 0, None)
		self.particle_link = name_type_map['Ref'](self.context, 0, name_type_map['NiObject'])

		# Timestamp of the last update.
		self.particle_timestamp = name_type_map['Uint'](self.context, 0, None)

		# Unknown short
		self.particle_unknown_short = name_type_map['Ushort'](self.context, 0, None)

		# Particle/vertex index matches array index
		self.particle_vertex_id = name_type_map['Ushort'](self.context, 0, None)

		# Size of the following array. (Maximum number of simultaneous active particles)
		self.num_particles = name_type_map['Ushort'](self.context, 0, None)

		# Number of valid entries in the following array. (Number of active particles at the time the system was saved)
		self.num_valid = name_type_map['Ushort'](self.context, 0, None)
		self.particles = Array(self.context, 0, None, (0,), name_type_map['NiParticleInfo'])
		self.emitter_modifier = name_type_map['Ref'](self.context, 0, name_type_map['NiEmitterModifier'])

		# Link to some optional particle modifiers (NiGravity, NiParticleGrowFade, NiParticleBomb, ...)
		self.particle_modifier = name_type_map['Ref'](self.context, 0, name_type_map['NiParticleModifier'])
		self.particle_collider = name_type_map['Ref'](self.context, 0, name_type_map['NiParticleCollider'])
		self.static_target_bound = name_type_map['Byte'](self.context, 0, None)
		self.color_data = name_type_map['Ref'](self.context, 0, name_type_map['NiColorData'])
		self.unknown_float_1 = name_type_map['Float'](self.context, 0, None)
		self.unknown_floats_2 = Array(self.context, 0, None, (0,), name_type_map['Float'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'old_speed', name_type_map['Uint'], (0, None), (False, None), (lambda context: context.version <= 50397184, None)
		yield 'speed', name_type_map['Float'], (0, None), (False, None), (lambda context: context.version >= 50528269, None)
		yield 'speed_variation', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'declination', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'declination_variation', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'planar_angle', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'planar_angle_variation', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'initial_normal', name_type_map['Vector3'], (0, None), (False, (1.0, 0.0, 0.0)), (None, None)
		yield 'initial_color', name_type_map['Color4'], (0, None), (False, (1.0, 1.0, 1.0, 1.0)), (None, None)
		yield 'initial_size', name_type_map['Float'], (0, None), (False, 1.0), (None, None)
		yield 'emit_start_time', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'emit_stop_time', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'reset_particle_system', name_type_map['Byte'], (0, None), (False, None), (lambda context: context.version >= 50528269, None)
		yield 'old_emit_rate', name_type_map['Uint'], (0, None), (False, None), (lambda context: context.version <= 50397184, None)
		yield 'birth_rate', name_type_map['Float'], (0, None), (False, None), (lambda context: context.version >= 50528269, None)
		yield 'lifetime', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'lifetime_variation', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'use_birth_rate', name_type_map['Byte'], (0, None), (False, None), (lambda context: context.version >= 50528269, None)
		yield 'spawn_on_death', name_type_map['Byte'], (0, None), (False, None), (lambda context: context.version >= 50528269, None)
		yield 'emitter_dimensions', name_type_map['Vector3'], (0, None), (False, None), (None, None)
		yield 'emitter', name_type_map['Ptr'], (0, name_type_map['NiAVObject']), (False, None), (None, None)
		yield 'num_spawn_generations', name_type_map['Ushort'], (0, None), (False, 1), (lambda context: context.version >= 50528269, None)
		yield 'percentage_spawned', name_type_map['Float'], (0, None), (False, 1.0), (lambda context: context.version >= 50528269, None)
		yield 'spawn_multiplier', name_type_map['Ushort'], (0, None), (False, None), (lambda context: context.version >= 50528269, None)
		yield 'spawn_speed_chaos', name_type_map['Float'], (0, None), (False, None), (lambda context: context.version >= 50528269, None)
		yield 'spawn_dir_chaos', name_type_map['Float'], (0, None), (False, None), (lambda context: context.version >= 50528269, None)
		yield 'particle_velocity', name_type_map['Vector3'], (0, None), (False, None), (lambda context: context.version <= 50397184, None)
		yield 'particle_unknown_vector', name_type_map['Vector3'], (0, None), (False, None), (lambda context: context.version <= 50397184, None)
		yield 'particle_lifetime', name_type_map['Float'], (0, None), (False, None), (lambda context: context.version <= 50397184, None)
		yield 'particle_link', name_type_map['Ref'], (0, name_type_map['NiObject']), (False, None), (lambda context: context.version <= 50397184, None)
		yield 'particle_timestamp', name_type_map['Uint'], (0, None), (False, None), (lambda context: context.version <= 50397184, None)
		yield 'particle_unknown_short', name_type_map['Ushort'], (0, None), (False, None), (lambda context: context.version <= 50397184, None)
		yield 'particle_vertex_id', name_type_map['Ushort'], (0, None), (False, None), (lambda context: context.version <= 50397184, None)
		yield 'num_particles', name_type_map['Ushort'], (0, None), (False, None), (lambda context: context.version >= 50528269, None)
		yield 'num_valid', name_type_map['Ushort'], (0, None), (False, None), (lambda context: context.version >= 50528269, None)
		yield 'particles', Array, (0, None, (None,), name_type_map['NiParticleInfo']), (False, None), (lambda context: context.version >= 50528269, None)
		yield 'emitter_modifier', name_type_map['Ref'], (0, name_type_map['NiEmitterModifier']), (False, None), (lambda context: context.version >= 50528269, None)
		yield 'particle_modifier', name_type_map['Ref'], (0, name_type_map['NiParticleModifier']), (False, None), (None, None)
		yield 'particle_collider', name_type_map['Ref'], (0, name_type_map['NiParticleCollider']), (False, None), (None, None)
		yield 'static_target_bound', name_type_map['Byte'], (0, None), (False, None), (lambda context: context.version >= 50528271, None)
		yield 'color_data', name_type_map['Ref'], (0, name_type_map['NiColorData']), (False, None), (lambda context: context.version <= 50397184, None)
		yield 'unknown_float_1', name_type_map['Float'], (0, None), (False, None), (lambda context: context.version <= 50397184, None)
		yield 'unknown_floats_2', Array, (0, None, (None,), name_type_map['Float']), (False, None), (lambda context: context.version <= 50397184, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		if instance.context.version <= 50397184:
			yield 'old_speed', name_type_map['Uint'], (0, None), (False, None)
		if instance.context.version >= 50528269:
			yield 'speed', name_type_map['Float'], (0, None), (False, None)
		yield 'speed_variation', name_type_map['Float'], (0, None), (False, None)
		yield 'declination', name_type_map['Float'], (0, None), (False, None)
		yield 'declination_variation', name_type_map['Float'], (0, None), (False, None)
		yield 'planar_angle', name_type_map['Float'], (0, None), (False, None)
		yield 'planar_angle_variation', name_type_map['Float'], (0, None), (False, None)
		yield 'initial_normal', name_type_map['Vector3'], (0, None), (False, (1.0, 0.0, 0.0))
		yield 'initial_color', name_type_map['Color4'], (0, None), (False, (1.0, 1.0, 1.0, 1.0))
		yield 'initial_size', name_type_map['Float'], (0, None), (False, 1.0)
		yield 'emit_start_time', name_type_map['Float'], (0, None), (False, None)
		yield 'emit_stop_time', name_type_map['Float'], (0, None), (False, None)
		if instance.context.version >= 50528269:
			yield 'reset_particle_system', name_type_map['Byte'], (0, None), (False, None)
		if instance.context.version <= 50397184:
			yield 'old_emit_rate', name_type_map['Uint'], (0, None), (False, None)
		if instance.context.version >= 50528269:
			yield 'birth_rate', name_type_map['Float'], (0, None), (False, None)
		yield 'lifetime', name_type_map['Float'], (0, None), (False, None)
		yield 'lifetime_variation', name_type_map['Float'], (0, None), (False, None)
		if instance.context.version >= 50528269:
			yield 'use_birth_rate', name_type_map['Byte'], (0, None), (False, None)
			yield 'spawn_on_death', name_type_map['Byte'], (0, None), (False, None)
		yield 'emitter_dimensions', name_type_map['Vector3'], (0, None), (False, None)
		yield 'emitter', name_type_map['Ptr'], (0, name_type_map['NiAVObject']), (False, None)
		if instance.context.version >= 50528269:
			yield 'num_spawn_generations', name_type_map['Ushort'], (0, None), (False, 1)
			yield 'percentage_spawned', name_type_map['Float'], (0, None), (False, 1.0)
			yield 'spawn_multiplier', name_type_map['Ushort'], (0, None), (False, None)
			yield 'spawn_speed_chaos', name_type_map['Float'], (0, None), (False, None)
			yield 'spawn_dir_chaos', name_type_map['Float'], (0, None), (False, None)
		if instance.context.version <= 50397184:
			yield 'particle_velocity', name_type_map['Vector3'], (0, None), (False, None)
			yield 'particle_unknown_vector', name_type_map['Vector3'], (0, None), (False, None)
			yield 'particle_lifetime', name_type_map['Float'], (0, None), (False, None)
			yield 'particle_link', name_type_map['Ref'], (0, name_type_map['NiObject']), (False, None)
			yield 'particle_timestamp', name_type_map['Uint'], (0, None), (False, None)
			yield 'particle_unknown_short', name_type_map['Ushort'], (0, None), (False, None)
			yield 'particle_vertex_id', name_type_map['Ushort'], (0, None), (False, None)
		if instance.context.version >= 50528269:
			yield 'num_particles', name_type_map['Ushort'], (0, None), (False, None)
			yield 'num_valid', name_type_map['Ushort'], (0, None), (False, None)
			yield 'particles', Array, (0, None, (instance.num_particles,), name_type_map['NiParticleInfo']), (False, None)
			yield 'emitter_modifier', name_type_map['Ref'], (0, name_type_map['NiEmitterModifier']), (False, None)
		yield 'particle_modifier', name_type_map['Ref'], (0, name_type_map['NiParticleModifier']), (False, None)
		yield 'particle_collider', name_type_map['Ref'], (0, name_type_map['NiParticleCollider']), (False, None)
		if instance.context.version >= 50528271:
			yield 'static_target_bound', name_type_map['Byte'], (0, None), (False, None)
		if instance.context.version <= 50397184:
			yield 'color_data', name_type_map['Ref'], (0, name_type_map['NiColorData']), (False, None)
			yield 'unknown_float_1', name_type_map['Float'], (0, None), (False, None)
			yield 'unknown_floats_2', Array, (0, None, (instance.particle_unknown_short,), name_type_map['Float']), (False, None)

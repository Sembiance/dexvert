from nifgen.array import Array
from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.niparticle.niobjects.NiPSysModifier import NiPSysModifier


class NiPSysEmitter(NiPSysModifier):

	"""
	Abstract base class for all particle system emitters.
	"""

	__name__ = 'NiPSysEmitter'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# Speed / Inertia of particle movement.
		self.speed = name_type_map['Float'](self.context, 0, None)

		# Adds an amount of randomness to Speed.
		self.speed_variation = name_type_map['Float'](self.context, 0, None)

		# Declination / First axis.
		self.declination = name_type_map['Float'](self.context, 0, None)

		# Declination randomness / First axis.
		self.declination_variation = name_type_map['Float'](self.context, 0, None)

		# Planar Angle / Second axis.
		self.planar_angle = name_type_map['Float'](self.context, 0, None)

		# Planar Angle randomness / Second axis .
		self.planar_angle_variation = name_type_map['Float'](self.context, 0, None)

		# Defines color of a birthed particle.
		self.initial_color = name_type_map['Color4'].from_value((1.0, 1.0, 1.0, 1.0))

		# Size of a birthed particle.
		self.initial_radius = name_type_map['Float'].from_value(1.0)

		# Particle Radius randomness.
		self.radius_variation = name_type_map['Float'](self.context, 0, None)

		# Duration until a particle dies.
		self.life_span = name_type_map['Float'](self.context, 0, None)

		# Adds randomness to Life Span.
		self.life_span_variation = name_type_map['Float'](self.context, 0, None)

		# Both 1.0 in example nif.
		self.unknown_q_q_speed_floats = Array(self.context, 0, None, (0,), name_type_map['Float'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'speed', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'speed_variation', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'declination', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'declination_variation', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'planar_angle', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'planar_angle_variation', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'initial_color', name_type_map['Color4'], (0, None), (False, (1.0, 1.0, 1.0, 1.0)), (None, None)
		yield 'initial_radius', name_type_map['Float'], (0, None), (False, 1.0), (None, None)
		yield 'radius_variation', name_type_map['Float'], (0, None), (False, None), (lambda context: context.version >= 168034305, None)
		yield 'life_span', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'life_span_variation', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'unknown_q_q_speed_floats', Array, (0, None, (2,), name_type_map['Float']), (False, None), (lambda context: 335676423 <= context.version <= 335676423, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'speed', name_type_map['Float'], (0, None), (False, None)
		yield 'speed_variation', name_type_map['Float'], (0, None), (False, None)
		yield 'declination', name_type_map['Float'], (0, None), (False, None)
		yield 'declination_variation', name_type_map['Float'], (0, None), (False, None)
		yield 'planar_angle', name_type_map['Float'], (0, None), (False, None)
		yield 'planar_angle_variation', name_type_map['Float'], (0, None), (False, None)
		yield 'initial_color', name_type_map['Color4'], (0, None), (False, (1.0, 1.0, 1.0, 1.0))
		yield 'initial_radius', name_type_map['Float'], (0, None), (False, 1.0)
		if instance.context.version >= 168034305:
			yield 'radius_variation', name_type_map['Float'], (0, None), (False, None)
		yield 'life_span', name_type_map['Float'], (0, None), (False, None)
		yield 'life_span_variation', name_type_map['Float'], (0, None), (False, None)
		if 335676423 <= instance.context.version <= 335676423:
			yield 'unknown_q_q_speed_floats', Array, (0, None, (2,), name_type_map['Float']), (False, None)

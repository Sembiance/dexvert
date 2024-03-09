from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.niparticle.niobjects.NiPSysModifier import NiPSysModifier


class NiPSysGravityModifier(NiPSysModifier):

	"""
	Particle modifier that applies a gravitational force to particles.
	"""

	__name__ = 'NiPSysGravityModifier'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# The object whose position and orientation are the basis of the force.
		self.gravity_object = name_type_map['Ptr'](self.context, 0, name_type_map['NiAVObject'])

		# The local direction of the force.
		self.gravity_axis = name_type_map['Vector3'].from_value((1.0, 0.0, 0.0))

		# How the force diminishes by distance.
		self.decay = name_type_map['Float'](self.context, 0, None)

		# The acceleration of the force.
		self.strength = name_type_map['Float'].from_value(1.0)

		# The type of gravitational force.
		self.force_type = name_type_map['ForceType'](self.context, 0, None)

		# Adds a degree of randomness.
		self.turbulence = name_type_map['Float'](self.context, 0, None)

		# Scale for turbulence.
		self.turbulence_scale = name_type_map['Float'].from_value(1.0)
		self.world_aligned = name_type_map['Bool'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'gravity_object', name_type_map['Ptr'], (0, name_type_map['NiAVObject']), (False, None), (None, None)
		yield 'gravity_axis', name_type_map['Vector3'], (0, None), (False, (1.0, 0.0, 0.0)), (None, None)
		yield 'decay', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'strength', name_type_map['Float'], (0, None), (False, 1.0), (None, None)
		yield 'force_type', name_type_map['ForceType'], (0, None), (False, None), (None, None)
		yield 'turbulence', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'turbulence_scale', name_type_map['Float'], (0, None), (False, 1.0), (None, None)
		yield 'world_aligned', name_type_map['Bool'], (0, None), (False, None), (lambda context: not (context.bs_header.bs_version <= 16), None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'gravity_object', name_type_map['Ptr'], (0, name_type_map['NiAVObject']), (False, None)
		yield 'gravity_axis', name_type_map['Vector3'], (0, None), (False, (1.0, 0.0, 0.0))
		yield 'decay', name_type_map['Float'], (0, None), (False, None)
		yield 'strength', name_type_map['Float'], (0, None), (False, 1.0)
		yield 'force_type', name_type_map['ForceType'], (0, None), (False, None)
		yield 'turbulence', name_type_map['Float'], (0, None), (False, None)
		yield 'turbulence_scale', name_type_map['Float'], (0, None), (False, 1.0)
		if not (instance.context.bs_header.bs_version <= 16):
			yield 'world_aligned', name_type_map['Bool'], (0, None), (False, None)

from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.niparticle.niobjects.NiPSysFieldModifier import NiPSysFieldModifier


class NiPSysAirFieldModifier(NiPSysFieldModifier):

	"""
	Particle system modifier, updates the particle velocity to simulate the effects of air movements like wind, fans, or wake.
	"""

	__name__ = 'NiPSysAirFieldModifier'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# Direction of the particle velocity
		self.direction = name_type_map['Vector3'].from_value((-1.0, 0.0, 0.0))

		# How quickly particles will accelerate to the magnitude of the air field.
		self.air_friction = name_type_map['Float'](self.context, 0, None)

		# How much of the air field velocity will be added to the particle velocity.
		self.inherit_velocity = name_type_map['Float'](self.context, 0, None)
		self.inherit_rotation = name_type_map['Bool'](self.context, 0, None)
		self.component_only = name_type_map['Bool'](self.context, 0, None)
		self.enable_spread = name_type_map['Bool'](self.context, 0, None)

		# The angle of the air field cone if Enable Spread is true.
		self.spread = name_type_map['Float'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'direction', name_type_map['Vector3'], (0, None), (False, (-1.0, 0.0, 0.0)), (None, None)
		yield 'air_friction', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'inherit_velocity', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'inherit_rotation', name_type_map['Bool'], (0, None), (False, None), (None, None)
		yield 'component_only', name_type_map['Bool'], (0, None), (False, None), (None, None)
		yield 'enable_spread', name_type_map['Bool'], (0, None), (False, None), (None, None)
		yield 'spread', name_type_map['Float'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'direction', name_type_map['Vector3'], (0, None), (False, (-1.0, 0.0, 0.0))
		yield 'air_friction', name_type_map['Float'], (0, None), (False, None)
		yield 'inherit_velocity', name_type_map['Float'], (0, None), (False, None)
		yield 'inherit_rotation', name_type_map['Bool'], (0, None), (False, None)
		yield 'component_only', name_type_map['Bool'], (0, None), (False, None)
		yield 'enable_spread', name_type_map['Bool'], (0, None), (False, None)
		yield 'spread', name_type_map['Float'], (0, None), (False, None)

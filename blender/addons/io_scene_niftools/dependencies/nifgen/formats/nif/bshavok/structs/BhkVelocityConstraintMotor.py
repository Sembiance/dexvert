from nifgen.base_struct import BaseStruct
from nifgen.formats.nif.imports import name_type_map


class BhkVelocityConstraintMotor(BaseStruct):

	"""
	Bethesda extension of hkpVelocityConstraintMotor. Tries to reach and keep a desired target velocity.
	"""

	__name__ = 'bhkVelocityConstraintMotor'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# Minimum motor force
		self.min_force = name_type_map['Float'].from_value(-1000000.0)

		# Maximum motor force
		self.max_force = name_type_map['Float'].from_value(1000000.0)

		# Relative stiffness
		self.tau = name_type_map['Float'].from_value(0.0)
		self.target_velocity = name_type_map['Float'].from_value(0.0)
		self.use_velocity_target = name_type_map['Bool'].from_value(False)

		# Is Motor enabled
		self.motor_enabled = name_type_map['Bool'].from_value(False)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'min_force', name_type_map['Float'], (0, None), (False, -1000000.0), (None, None)
		yield 'max_force', name_type_map['Float'], (0, None), (False, 1000000.0), (None, None)
		yield 'tau', name_type_map['Float'], (0, None), (False, 0.0), (None, None)
		yield 'target_velocity', name_type_map['Float'], (0, None), (False, 0.0), (None, None)
		yield 'use_velocity_target', name_type_map['Bool'], (0, None), (False, False), (None, None)
		yield 'motor_enabled', name_type_map['Bool'], (0, None), (False, False), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'min_force', name_type_map['Float'], (0, None), (False, -1000000.0)
		yield 'max_force', name_type_map['Float'], (0, None), (False, 1000000.0)
		yield 'tau', name_type_map['Float'], (0, None), (False, 0.0)
		yield 'target_velocity', name_type_map['Float'], (0, None), (False, 0.0)
		yield 'use_velocity_target', name_type_map['Bool'], (0, None), (False, False)
		yield 'motor_enabled', name_type_map['Bool'], (0, None), (False, False)

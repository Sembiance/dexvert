from nifgen.base_struct import BaseStruct
from nifgen.formats.nif.imports import name_type_map


class BhkPositionConstraintMotor(BaseStruct):

	"""
	Bethesda extension of hkpPositionConstraintMotor.
	A motor which tries to reach a desired position/angle given a max force and recovery speed.
	This motor is a good choice for driving a ragdoll to a given pose.
	"""

	__name__ = 'bhkPositionConstraintMotor'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# Minimum motor force
		self.min_force = name_type_map['Float'].from_value(-1000000.0)

		# Maximum motor force
		self.max_force = name_type_map['Float'].from_value(1000000.0)

		# Relative stiffness
		self.tau = name_type_map['Float'].from_value(0.8)

		# Motor damping value
		self.damping = name_type_map['Float'].from_value(1.0)

		# A factor of the current error to calculate the recovery velocity
		self.proportional_recovery_velocity = name_type_map['Float'].from_value(2.0)

		# A constant velocity which is used to recover from errors
		self.constant_recovery_velocity = name_type_map['Float'].from_value(1.0)

		# Is Motor enabled
		self.motor_enabled = name_type_map['Bool'].from_value(False)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'min_force', name_type_map['Float'], (0, None), (False, -1000000.0), (None, None)
		yield 'max_force', name_type_map['Float'], (0, None), (False, 1000000.0), (None, None)
		yield 'tau', name_type_map['Float'], (0, None), (False, 0.8), (None, None)
		yield 'damping', name_type_map['Float'], (0, None), (False, 1.0), (None, None)
		yield 'proportional_recovery_velocity', name_type_map['Float'], (0, None), (False, 2.0), (None, None)
		yield 'constant_recovery_velocity', name_type_map['Float'], (0, None), (False, 1.0), (None, None)
		yield 'motor_enabled', name_type_map['Bool'], (0, None), (False, False), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'min_force', name_type_map['Float'], (0, None), (False, -1000000.0)
		yield 'max_force', name_type_map['Float'], (0, None), (False, 1000000.0)
		yield 'tau', name_type_map['Float'], (0, None), (False, 0.8)
		yield 'damping', name_type_map['Float'], (0, None), (False, 1.0)
		yield 'proportional_recovery_velocity', name_type_map['Float'], (0, None), (False, 2.0)
		yield 'constant_recovery_velocity', name_type_map['Float'], (0, None), (False, 1.0)
		yield 'motor_enabled', name_type_map['Bool'], (0, None), (False, False)

from nifgen.base_struct import BaseStruct
from nifgen.formats.nif.imports import name_type_map


class BhkSpringDamperConstraintMotor(BaseStruct):

	"""
	Bethesda extension of hkpSpringDamperConstraintMotor.
	Tries to reach a given target position using an angular spring which has a spring constant.
	"""

	__name__ = 'bhkSpringDamperConstraintMotor'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# Minimum motor force
		self.min_force = name_type_map['Float'].from_value(-1000000.0)

		# Maximum motor force
		self.max_force = name_type_map['Float'].from_value(1000000.0)

		# The spring constant in N/m
		self.spring_constant = name_type_map['Float'].from_value(0.0)

		# The spring damping in Nsec/m
		self.spring_damping = name_type_map['Float'].from_value(0.0)

		# Is Motor enabled
		self.motor_enabled = name_type_map['Bool'].from_value(False)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'min_force', name_type_map['Float'], (0, None), (False, -1000000.0), (None, None)
		yield 'max_force', name_type_map['Float'], (0, None), (False, 1000000.0), (None, None)
		yield 'spring_constant', name_type_map['Float'], (0, None), (False, 0.0), (None, None)
		yield 'spring_damping', name_type_map['Float'], (0, None), (False, 0.0), (None, None)
		yield 'motor_enabled', name_type_map['Bool'], (0, None), (False, False), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'min_force', name_type_map['Float'], (0, None), (False, -1000000.0)
		yield 'max_force', name_type_map['Float'], (0, None), (False, 1000000.0)
		yield 'spring_constant', name_type_map['Float'], (0, None), (False, 0.0)
		yield 'spring_damping', name_type_map['Float'], (0, None), (False, 0.0)
		yield 'motor_enabled', name_type_map['Bool'], (0, None), (False, False)

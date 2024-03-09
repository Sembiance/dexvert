from nifgen.base_struct import BaseStruct
from nifgen.formats.nif.imports import name_type_map


class BhkConstraintMotorCInfo(BaseStruct):

	"""
	hkConstraintCinfo::SaveMotor(). Not a Bethesda extension of hkpConstraintMotor, but a wrapper for its serialization function.
	"""

	__name__ = 'bhkConstraintMotorCInfo'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.type = name_type_map['HkMotorType'].MOTOR_NONE
		self.position_motor = name_type_map['BhkPositionConstraintMotor'](self.context, 0, None)
		self.velocity_motor = name_type_map['BhkVelocityConstraintMotor'](self.context, 0, None)
		self.spring_damper_motor = name_type_map['BhkSpringDamperConstraintMotor'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'type', name_type_map['HkMotorType'], (0, None), (False, name_type_map['HkMotorType'].MOTOR_NONE), (None, None)
		yield 'position_motor', name_type_map['BhkPositionConstraintMotor'], (0, None), (False, None), (None, True)
		yield 'velocity_motor', name_type_map['BhkVelocityConstraintMotor'], (0, None), (False, None), (None, True)
		yield 'spring_damper_motor', name_type_map['BhkSpringDamperConstraintMotor'], (0, None), (False, None), (None, True)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'type', name_type_map['HkMotorType'], (0, None), (False, name_type_map['HkMotorType'].MOTOR_NONE)
		if instance.type == 1:
			yield 'position_motor', name_type_map['BhkPositionConstraintMotor'], (0, None), (False, None)
		if instance.type == 2:
			yield 'velocity_motor', name_type_map['BhkVelocityConstraintMotor'], (0, None), (False, None)
		if instance.type == 3:
			yield 'spring_damper_motor', name_type_map['BhkSpringDamperConstraintMotor'], (0, None), (False, None)

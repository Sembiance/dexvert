from nifgen.array import Array
from nifgen.base_struct import BaseStruct
from nifgen.formats.nif.imports import name_type_map


class BhkRigidBodyCInfo2014(BaseStruct):

	__name__ = 'bhkRigidBodyCInfo2014'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.unused_01 = Array(self.context, 0, None, (0,), name_type_map['Byte'])
		self.havok_filter = name_type_map['HavokFilter'](self.context, 0, None)
		self.unused_02 = Array(self.context, 0, None, (0,), name_type_map['Byte'])

		# A vector that moves the body by the specified amount. Only enabled in bhkRigidBodyT objects.
		self.translation = name_type_map['Vector4'](self.context, 0, None)

		# The rotation Yaw/Pitch/Roll to apply to the body. Only enabled in bhkRigidBodyT objects.
		self.rotation = name_type_map['HkQuaternion'](self.context, 0, None)

		# Linear velocity.
		self.linear_velocity = name_type_map['Vector4'](self.context, 0, None)

		# Angular velocity.
		self.angular_velocity = name_type_map['Vector4'](self.context, 0, None)

		# Defines how the mass is distributed among the body, i.e. how difficult it is to rotate around any given axis.
		self.inertia_tensor = name_type_map['HkMatrix3'](self.context, 0, None)

		# The body's center of mass.
		self.center = name_type_map['Vector4'](self.context, 0, None)

		# The body's mass in kg. A mass of zero represents an immovable object.
		self.mass = name_type_map['Float'].from_value(1.0)

		# Reduces the movement of the body over time. A value of 0.1 will remove 10% of the linear velocity every second.
		self.linear_damping = name_type_map['Float'].from_value(0.1)

		# Reduces the movement of the body over time. A value of 0.05 will remove 5% of the angular velocity every second.
		self.angular_damping = name_type_map['Float'].from_value(0.05)
		self.gravity_factor = name_type_map['Float'].from_value(1.0)

		# How smooth its surfaces is and how easily it will slide along other bodies.
		self.friction = name_type_map['Float'].from_value(0.5)
		self.rolling_friction_multiplier = name_type_map['Float'](self.context, 0, None)

		# How "bouncy" the body is, i.e. how much energy it has after colliding. Less than 1.0 loses energy, greater than 1.0 gains energy.
		# If the restitution is not 0.0 the object will need extra CPU for all new collisions.
		self.restitution = name_type_map['Float'].from_value(0.4)

		# Maximal linear velocity.
		self.max_linear_velocity = name_type_map['Float'].from_value(104.4)

		# Maximal angular velocity.
		self.max_angular_velocity = name_type_map['Float'].from_value(31.57)

		# Motion system? Overrides Quality when on Keyframed?
		self.motion_system = name_type_map['HkMotionType'].MO_SYS_DYNAMIC

		# The initial deactivator type of the body.
		self.deactivator_type = name_type_map['HkDeactivatorType'].DEACTIVATOR_NEVER

		# How aggressively the engine will try to zero the velocity for slow objects. This does not save CPU.
		self.solver_deactivation = name_type_map['HkSolverDeactivation'].SOLVER_DEACTIVATION_OFF
		self.unused_03 = name_type_map['Byte'](self.context, 0, None)

		# The maximum allowed penetration for this object.
		# This is a hint to the engine to see how much CPU the engine should invest to keep this object from penetrating.
		# A good choice is 5% - 20% of the smallest diameter of the object.
		self.penetration_depth = name_type_map['Float'].from_value(0.15)
		self.time_factor = name_type_map['Float'](self.context, 0, None)
		self.unused_04 = Array(self.context, 0, None, (0,), name_type_map['Byte'])
		self.collision_response = name_type_map['HkResponseType'](self.context, 0, None)
		self.unused_05 = name_type_map['Byte'](self.context, 0, None)
		self.process_contact_callback_delay_3 = name_type_map['Ushort'].from_value(65535)
		self.quality_type = name_type_map['HkQualityType'].MO_QUAL_FIXED
		self.auto_remove_level = name_type_map['Byte'](self.context, 0, None)
		self.response_modifier_flags = name_type_map['Byte'](self.context, 0, None)
		self.num_shape_keys_in_contact_point = name_type_map['Byte'].from_value(3)
		self.force_collided_onto_ppu = name_type_map['Bool'](self.context, 0, None)
		self.unused_06 = Array(self.context, 0, None, (0,), name_type_map['Byte'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'unused_01', Array, (0, None, (4,), name_type_map['Byte']), (False, None), (None, None)
		yield 'havok_filter', name_type_map['HavokFilter'], (0, None), (False, None), (None, None)
		yield 'unused_02', Array, (0, None, (12,), name_type_map['Byte']), (False, None), (None, None)
		yield 'translation', name_type_map['Vector4'], (0, None), (False, None), (None, None)
		yield 'rotation', name_type_map['HkQuaternion'], (0, None), (False, None), (None, None)
		yield 'linear_velocity', name_type_map['Vector4'], (0, None), (False, None), (None, None)
		yield 'angular_velocity', name_type_map['Vector4'], (0, None), (False, None), (None, None)
		yield 'inertia_tensor', name_type_map['HkMatrix3'], (0, None), (False, None), (None, None)
		yield 'center', name_type_map['Vector4'], (0, None), (False, None), (None, None)
		yield 'mass', name_type_map['Float'], (0, None), (False, 1.0), (None, None)
		yield 'linear_damping', name_type_map['Float'], (0, None), (False, 0.1), (None, None)
		yield 'angular_damping', name_type_map['Float'], (0, None), (False, 0.05), (None, None)
		yield 'gravity_factor', name_type_map['Float'], (0, None), (False, 1.0), (None, None)
		yield 'friction', name_type_map['Float'], (0, None), (False, 0.5), (None, None)
		yield 'rolling_friction_multiplier', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'restitution', name_type_map['Float'], (0, None), (False, 0.4), (None, None)
		yield 'max_linear_velocity', name_type_map['Float'], (0, None), (False, 104.4), (None, None)
		yield 'max_angular_velocity', name_type_map['Float'], (0, None), (False, 31.57), (None, None)
		yield 'motion_system', name_type_map['HkMotionType'], (0, None), (False, name_type_map['HkMotionType'].MO_SYS_DYNAMIC), (None, None)
		yield 'deactivator_type', name_type_map['HkDeactivatorType'], (0, None), (False, name_type_map['HkDeactivatorType'].DEACTIVATOR_NEVER), (None, None)
		yield 'solver_deactivation', name_type_map['HkSolverDeactivation'], (0, None), (False, name_type_map['HkSolverDeactivation'].SOLVER_DEACTIVATION_OFF), (None, None)
		yield 'unused_03', name_type_map['Byte'], (0, None), (False, None), (None, None)
		yield 'penetration_depth', name_type_map['Float'], (0, None), (False, 0.15), (None, None)
		yield 'time_factor', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'unused_04', Array, (0, None, (4,), name_type_map['Byte']), (False, None), (None, None)
		yield 'collision_response', name_type_map['HkResponseType'], (0, None), (False, None), (None, None)
		yield 'unused_05', name_type_map['Byte'], (0, None), (False, None), (None, None)
		yield 'process_contact_callback_delay_3', name_type_map['Ushort'], (0, None), (False, 65535), (None, None)
		yield 'quality_type', name_type_map['HkQualityType'], (0, None), (False, name_type_map['HkQualityType'].MO_QUAL_FIXED), (None, None)
		yield 'auto_remove_level', name_type_map['Byte'], (0, None), (False, None), (None, None)
		yield 'response_modifier_flags', name_type_map['Byte'], (0, None), (False, None), (None, None)
		yield 'num_shape_keys_in_contact_point', name_type_map['Byte'], (0, None), (False, 3), (None, None)
		yield 'force_collided_onto_ppu', name_type_map['Bool'], (0, None), (False, None), (None, None)
		yield 'unused_06', Array, (0, None, (3,), name_type_map['Byte']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'unused_01', Array, (0, None, (4,), name_type_map['Byte']), (False, None)
		yield 'havok_filter', name_type_map['HavokFilter'], (0, None), (False, None)
		yield 'unused_02', Array, (0, None, (12,), name_type_map['Byte']), (False, None)
		yield 'translation', name_type_map['Vector4'], (0, None), (False, None)
		yield 'rotation', name_type_map['HkQuaternion'], (0, None), (False, None)
		yield 'linear_velocity', name_type_map['Vector4'], (0, None), (False, None)
		yield 'angular_velocity', name_type_map['Vector4'], (0, None), (False, None)
		yield 'inertia_tensor', name_type_map['HkMatrix3'], (0, None), (False, None)
		yield 'center', name_type_map['Vector4'], (0, None), (False, None)
		yield 'mass', name_type_map['Float'], (0, None), (False, 1.0)
		yield 'linear_damping', name_type_map['Float'], (0, None), (False, 0.1)
		yield 'angular_damping', name_type_map['Float'], (0, None), (False, 0.05)
		yield 'gravity_factor', name_type_map['Float'], (0, None), (False, 1.0)
		yield 'friction', name_type_map['Float'], (0, None), (False, 0.5)
		yield 'rolling_friction_multiplier', name_type_map['Float'], (0, None), (False, None)
		yield 'restitution', name_type_map['Float'], (0, None), (False, 0.4)
		yield 'max_linear_velocity', name_type_map['Float'], (0, None), (False, 104.4)
		yield 'max_angular_velocity', name_type_map['Float'], (0, None), (False, 31.57)
		yield 'motion_system', name_type_map['HkMotionType'], (0, None), (False, name_type_map['HkMotionType'].MO_SYS_DYNAMIC)
		yield 'deactivator_type', name_type_map['HkDeactivatorType'], (0, None), (False, name_type_map['HkDeactivatorType'].DEACTIVATOR_NEVER)
		yield 'solver_deactivation', name_type_map['HkSolverDeactivation'], (0, None), (False, name_type_map['HkSolverDeactivation'].SOLVER_DEACTIVATION_OFF)
		yield 'unused_03', name_type_map['Byte'], (0, None), (False, None)
		yield 'penetration_depth', name_type_map['Float'], (0, None), (False, 0.15)
		yield 'time_factor', name_type_map['Float'], (0, None), (False, None)
		yield 'unused_04', Array, (0, None, (4,), name_type_map['Byte']), (False, None)
		yield 'collision_response', name_type_map['HkResponseType'], (0, None), (False, None)
		yield 'unused_05', name_type_map['Byte'], (0, None), (False, None)
		yield 'process_contact_callback_delay_3', name_type_map['Ushort'], (0, None), (False, 65535)
		yield 'quality_type', name_type_map['HkQualityType'], (0, None), (False, name_type_map['HkQualityType'].MO_QUAL_FIXED)
		yield 'auto_remove_level', name_type_map['Byte'], (0, None), (False, None)
		yield 'response_modifier_flags', name_type_map['Byte'], (0, None), (False, None)
		yield 'num_shape_keys_in_contact_point', name_type_map['Byte'], (0, None), (False, 3)
		yield 'force_collided_onto_ppu', name_type_map['Bool'], (0, None), (False, None)
		yield 'unused_06', Array, (0, None, (3,), name_type_map['Byte']), (False, None)

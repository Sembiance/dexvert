from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.niphysx.niobjects.NiPhysXJointDesc import NiPhysXJointDesc


class NiPhysXD6JointDesc(NiPhysXJointDesc):

	"""
	A 6DOF (6 degrees of freedom) joint.
	"""

	__name__ = 'NiPhysXD6JointDesc'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.x_motion = name_type_map['NxD6JointMotion'].MOTION_FREE
		self.y_motion = name_type_map['NxD6JointMotion'].MOTION_FREE
		self.z_motion = name_type_map['NxD6JointMotion'].MOTION_FREE
		self.swing_1_motion = name_type_map['NxD6JointMotion'].MOTION_FREE
		self.swing_2_motion = name_type_map['NxD6JointMotion'].MOTION_FREE
		self.twist_motion = name_type_map['NxD6JointMotion'].MOTION_FREE
		self.linear_limit = name_type_map['NxJointLimitSoftDesc'](self.context, 0, None)
		self.swing_1_limit = name_type_map['NxJointLimitSoftDesc'](self.context, 0, None)
		self.swing_2_limit = name_type_map['NxJointLimitSoftDesc'](self.context, 0, None)
		self.twist_low_limit = name_type_map['NxJointLimitSoftDesc'](self.context, 0, None)
		self.twist_high_limit = name_type_map['NxJointLimitSoftDesc'](self.context, 0, None)
		self.x_drive = name_type_map['NxJointDriveDesc'](self.context, 0, None)
		self.y_drive = name_type_map['NxJointDriveDesc'](self.context, 0, None)
		self.z_drive = name_type_map['NxJointDriveDesc'](self.context, 0, None)
		self.swing_drive = name_type_map['NxJointDriveDesc'](self.context, 0, None)
		self.twist_drive = name_type_map['NxJointDriveDesc'](self.context, 0, None)
		self.slerp_drive = name_type_map['NxJointDriveDesc'](self.context, 0, None)
		self.drive_position = name_type_map['Vector3'](self.context, 0, None)
		self.drive_orientation = name_type_map['Quaternion'](self.context, 0, None)
		self.drive_linear_velocity = name_type_map['Vector3'](self.context, 0, None)
		self.drive_angular_velocity = name_type_map['Vector3'](self.context, 0, None)
		self.projection_mode = name_type_map['NxJointProjectionMode'](self.context, 0, None)
		self.projection_distance = name_type_map['Float'].from_value(0.1)
		self.projection_angle = name_type_map['Float'].from_value(0.0872)
		self.gear_ratio = name_type_map['Float'].from_value(1.0)
		self.flags = name_type_map['Uint'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'x_motion', name_type_map['NxD6JointMotion'], (0, None), (False, name_type_map['NxD6JointMotion'].MOTION_FREE), (None, None)
		yield 'y_motion', name_type_map['NxD6JointMotion'], (0, None), (False, name_type_map['NxD6JointMotion'].MOTION_FREE), (None, None)
		yield 'z_motion', name_type_map['NxD6JointMotion'], (0, None), (False, name_type_map['NxD6JointMotion'].MOTION_FREE), (None, None)
		yield 'swing_1_motion', name_type_map['NxD6JointMotion'], (0, None), (False, name_type_map['NxD6JointMotion'].MOTION_FREE), (None, None)
		yield 'swing_2_motion', name_type_map['NxD6JointMotion'], (0, None), (False, name_type_map['NxD6JointMotion'].MOTION_FREE), (None, None)
		yield 'twist_motion', name_type_map['NxD6JointMotion'], (0, None), (False, name_type_map['NxD6JointMotion'].MOTION_FREE), (None, None)
		yield 'linear_limit', name_type_map['NxJointLimitSoftDesc'], (0, None), (False, None), (None, None)
		yield 'swing_1_limit', name_type_map['NxJointLimitSoftDesc'], (0, None), (False, None), (None, None)
		yield 'swing_2_limit', name_type_map['NxJointLimitSoftDesc'], (0, None), (False, None), (None, None)
		yield 'twist_low_limit', name_type_map['NxJointLimitSoftDesc'], (0, None), (False, None), (None, None)
		yield 'twist_high_limit', name_type_map['NxJointLimitSoftDesc'], (0, None), (False, None), (None, None)
		yield 'x_drive', name_type_map['NxJointDriveDesc'], (0, None), (False, None), (None, None)
		yield 'y_drive', name_type_map['NxJointDriveDesc'], (0, None), (False, None), (None, None)
		yield 'z_drive', name_type_map['NxJointDriveDesc'], (0, None), (False, None), (None, None)
		yield 'swing_drive', name_type_map['NxJointDriveDesc'], (0, None), (False, None), (None, None)
		yield 'twist_drive', name_type_map['NxJointDriveDesc'], (0, None), (False, None), (None, None)
		yield 'slerp_drive', name_type_map['NxJointDriveDesc'], (0, None), (False, None), (None, None)
		yield 'drive_position', name_type_map['Vector3'], (0, None), (False, None), (None, None)
		yield 'drive_orientation', name_type_map['Quaternion'], (0, None), (False, None), (None, None)
		yield 'drive_linear_velocity', name_type_map['Vector3'], (0, None), (False, None), (None, None)
		yield 'drive_angular_velocity', name_type_map['Vector3'], (0, None), (False, None), (None, None)
		yield 'projection_mode', name_type_map['NxJointProjectionMode'], (0, None), (False, None), (None, None)
		yield 'projection_distance', name_type_map['Float'], (0, None), (False, 0.1), (None, None)
		yield 'projection_angle', name_type_map['Float'], (0, None), (False, 0.0872), (None, None)
		yield 'gear_ratio', name_type_map['Float'], (0, None), (False, 1.0), (None, None)
		yield 'flags', name_type_map['Uint'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'x_motion', name_type_map['NxD6JointMotion'], (0, None), (False, name_type_map['NxD6JointMotion'].MOTION_FREE)
		yield 'y_motion', name_type_map['NxD6JointMotion'], (0, None), (False, name_type_map['NxD6JointMotion'].MOTION_FREE)
		yield 'z_motion', name_type_map['NxD6JointMotion'], (0, None), (False, name_type_map['NxD6JointMotion'].MOTION_FREE)
		yield 'swing_1_motion', name_type_map['NxD6JointMotion'], (0, None), (False, name_type_map['NxD6JointMotion'].MOTION_FREE)
		yield 'swing_2_motion', name_type_map['NxD6JointMotion'], (0, None), (False, name_type_map['NxD6JointMotion'].MOTION_FREE)
		yield 'twist_motion', name_type_map['NxD6JointMotion'], (0, None), (False, name_type_map['NxD6JointMotion'].MOTION_FREE)
		yield 'linear_limit', name_type_map['NxJointLimitSoftDesc'], (0, None), (False, None)
		yield 'swing_1_limit', name_type_map['NxJointLimitSoftDesc'], (0, None), (False, None)
		yield 'swing_2_limit', name_type_map['NxJointLimitSoftDesc'], (0, None), (False, None)
		yield 'twist_low_limit', name_type_map['NxJointLimitSoftDesc'], (0, None), (False, None)
		yield 'twist_high_limit', name_type_map['NxJointLimitSoftDesc'], (0, None), (False, None)
		yield 'x_drive', name_type_map['NxJointDriveDesc'], (0, None), (False, None)
		yield 'y_drive', name_type_map['NxJointDriveDesc'], (0, None), (False, None)
		yield 'z_drive', name_type_map['NxJointDriveDesc'], (0, None), (False, None)
		yield 'swing_drive', name_type_map['NxJointDriveDesc'], (0, None), (False, None)
		yield 'twist_drive', name_type_map['NxJointDriveDesc'], (0, None), (False, None)
		yield 'slerp_drive', name_type_map['NxJointDriveDesc'], (0, None), (False, None)
		yield 'drive_position', name_type_map['Vector3'], (0, None), (False, None)
		yield 'drive_orientation', name_type_map['Quaternion'], (0, None), (False, None)
		yield 'drive_linear_velocity', name_type_map['Vector3'], (0, None), (False, None)
		yield 'drive_angular_velocity', name_type_map['Vector3'], (0, None), (False, None)
		yield 'projection_mode', name_type_map['NxJointProjectionMode'], (0, None), (False, None)
		yield 'projection_distance', name_type_map['Float'], (0, None), (False, 0.1)
		yield 'projection_angle', name_type_map['Float'], (0, None), (False, 0.0872)
		yield 'gear_ratio', name_type_map['Float'], (0, None), (False, 1.0)
		yield 'flags', name_type_map['Uint'], (0, None), (False, None)

from nifgen.bitfield import BasicBitfield
from nifgen.bitfield import BitfieldMember
from nifgen.formats.base.basic import Uint


class RagdollPhysicsActivityFlags(BasicBitfield):

	__name__ = 'RagdollPhysicsActivityFlags'
	_storage = Uint
	auto_sleep_enabled = BitfieldMember(pos=0, mask=0x1, return_type=int)
	collision_enabled = BitfieldMember(pos=1, mask=0x2, return_type=int)
	spatial_enabled = BitfieldMember(pos=2, mask=0x4, return_type=int)
	motor_driving_enabled = BitfieldMember(pos=3, mask=0x8, return_type=int)
	constraint_projection = BitfieldMember(pos=4, mask=0x10, return_type=int)
	activate_on_startup = BitfieldMember(pos=5, mask=0x20, return_type=int)
	activate_on_collision = BitfieldMember(pos=6, mask=0x40, return_type=int)
	activate_one_time_only = BitfieldMember(pos=7, mask=0x80, return_type=int)
	activate_by_data_stream = BitfieldMember(pos=8, mask=0x100, return_type=int)
	wake_on_activation = BitfieldMember(pos=9, mask=0x200, return_type=int)
	activation_disabled = BitfieldMember(pos=10, mask=0x400, return_type=int)
	lock_pose_on_activation = BitfieldMember(pos=11, mask=0x800, return_type=int)
	deactivate_pose_match = BitfieldMember(pos=12, mask=0x1000, return_type=int)
	motor_pose_matching = BitfieldMember(pos=13, mask=0x2000, return_type=int)
	motor_joint_stiffening = BitfieldMember(pos=14, mask=0x4000, return_type=int)
	force_sub_step_synch = BitfieldMember(pos=15, mask=0x8000, return_type=int)
	force_disable_synch = BitfieldMember(pos=16, mask=0x10000, return_type=int)
	force_callbacks = BitfieldMember(pos=17, mask=0x20000, return_type=int)

	def set_defaults(self):
		pass

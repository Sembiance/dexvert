from nifgen.formats.motiongraph.imports import name_type_map
from nifgen.formats.ovl_base.compounds.MemStruct import MemStruct


class RagdollPhysicsActivityData(MemStruct):

	"""
	? bytes
	"""

	__name__ = 'RagdollPhysicsActivityData'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.flag = name_type_map['RagdollPhysicsActivityFlags'](self.context, 0, None)
		self._flag_pad = name_type_map['Uint'](self.context, 0, None)
		self.collision_exclude_mask = name_type_map['Uint64'](self.context, 0, None)
		self.min_motor_driving_force = name_type_map['Float'](self.context, 0, None)
		self.max_motor_driving_force = name_type_map['Float'](self.context, 0, None)
		self.pose_match_lin_threshold = name_type_map['Float'](self.context, 0, None)
		self.pose_match_ang_threshold = name_type_map['Float'](self.context, 0, None)
		self.bone_chain_priority = name_type_map['Uint64'](self.context, 0, None)
		self.root_bone_name = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		self.collision_exclude_0 = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		self.collision_exclude_1 = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		self.collision_exclude_2 = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		self.collision_exclude_3 = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		self.collision_exclude_4 = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		self.collision_exclude_5 = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		self.collision_exclude_6 = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		self.collision_exclude_7 = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		self.motor_weight_variable = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		self.data_stream_name = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		self.data_stream_type = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'flag', name_type_map['RagdollPhysicsActivityFlags'], (0, None), (False, None), (None, None)
		yield '_flag_pad', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'root_bone_name', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'collision_exclude_mask', name_type_map['Uint64'], (0, None), (False, None), (None, None)
		yield 'collision_exclude_0', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'collision_exclude_1', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'collision_exclude_2', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'collision_exclude_3', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'collision_exclude_4', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'collision_exclude_5', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'collision_exclude_6', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'collision_exclude_7', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'min_motor_driving_force', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'max_motor_driving_force', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'motor_weight_variable', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'pose_match_lin_threshold', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'pose_match_ang_threshold', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'bone_chain_priority', name_type_map['Uint64'], (0, None), (False, None), (None, None)
		yield 'data_stream_name', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'data_stream_type', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'flag', name_type_map['RagdollPhysicsActivityFlags'], (0, None), (False, None)
		yield '_flag_pad', name_type_map['Uint'], (0, None), (False, None)
		yield 'root_bone_name', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'collision_exclude_mask', name_type_map['Uint64'], (0, None), (False, None)
		yield 'collision_exclude_0', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'collision_exclude_1', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'collision_exclude_2', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'collision_exclude_3', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'collision_exclude_4', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'collision_exclude_5', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'collision_exclude_6', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'collision_exclude_7', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'min_motor_driving_force', name_type_map['Float'], (0, None), (False, None)
		yield 'max_motor_driving_force', name_type_map['Float'], (0, None), (False, None)
		yield 'motor_weight_variable', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'pose_match_lin_threshold', name_type_map['Float'], (0, None), (False, None)
		yield 'pose_match_ang_threshold', name_type_map['Float'], (0, None), (False, None)
		yield 'bone_chain_priority', name_type_map['Uint64'], (0, None), (False, None)
		yield 'data_stream_name', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'data_stream_type', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)

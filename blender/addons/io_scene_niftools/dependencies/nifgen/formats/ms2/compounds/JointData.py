from nifgen.base_struct import BaseStruct
from nifgen.formats.ovl_base.basic import OffsetString
from nifgen.formats.ms2.compounds.JointPointer import JointPointer
import logging

from nifgen.array import Array
from nifgen.base_struct import BaseStruct
from nifgen.formats.ms2.imports import name_type_map


class JointData(BaseStruct):

	__name__ = 'JointData'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# seemingly additional alignment, unsure about the rule
		self.start_pc = name_type_map['SmartPadding'](self.context, 0, None)
		self.before_dla_0 = name_type_map['Uint64'](self.context, 0, None)
		self.before_dla_1 = name_type_map['Uint64'](self.context, 0, None)

		# repeat
		self.joint_count = name_type_map['Uint'](self.context, 0, None)
		self.num_push_constraints = name_type_map['Uint'](self.context, 0, None)
		self.num_stretch_constraints = name_type_map['Uint'](self.context, 0, None)
		self.num_ragdoll_constraints = name_type_map['Uint'](self.context, 0, None)
		self.zero_0 = name_type_map['Uint'](self.context, 0, None)
		self.zero_1 = name_type_map['Uint'](self.context, 0, None)

		# size of the name buffer below, including trailing zeros
		self.namespace_length = name_type_map['Uint'](self.context, 0, None)

		# 0s
		self.zeros_0 = Array(self.context, 0, None, (0,), name_type_map['Uint'])

		# 0 or 1
		self.pc_count = name_type_map['Uint'](self.context, 0, None)

		# 0s
		self.zeros_1 = Array(self.context, 0, None, (0,), name_type_map['Uint'])

		# 0s
		self.extra_zeros_2 = Array(self.context, 0, None, (0,), name_type_map['Uint'])
		self.one_0 = name_type_map['Uint64'].from_value(1)
		self.one_1 = name_type_map['Uint64'].from_value(1)

		# matches bone count from bone info
		self.bone_count = name_type_map['Uint'](self.context, 0, None)
		self.joint_entry_count = name_type_map['Uint'](self.context, 0, None)

		# usually 0s
		self.zeros_2 = Array(self.context, 0, None, (0,), name_type_map['Uint'])

		# usually 0s
		self.zeros_3 = name_type_map['Uint'](self.context, 0, None)
		self.names_ref = name_type_map['Empty'](self.context, 0, None)

		# corresponds to bone transforms
		self.joint_transforms = Array(self.context, 0, None, (0,), name_type_map['JointTransform'])
		self.rigid_body_pointers = Array(self.context, 0, None, (0,), name_type_map['Uint64'])
		self.rigid_body_list = Array(self.context, 0, None, (0,), name_type_map['RigidBody'])
		self.push_constraints = Array(self.context, 0, None, (0,), name_type_map['PushConstraint'])
		self.stretch_constraints = Array(self.context, 0, None, (0,), name_type_map['StretchConstraint'])
		self.ragdoll_constraints = Array(self.context, 0, None, (0,), name_type_map['RagdollConstraint'])

		# old style - joint infos, without hitchecks, they are added later
		self.joint_infos = Array(self.context, 0, None, (0,), name_type_map['UACJointFF'])

		# sometimes an array of floats
		self.pc_floats = Array(self.context, 0, None, (0,), name_type_map['Float'])
		self.names_ref_pc = name_type_map['Empty'](self.context, 0, None)

		# index into bone info bones for each joint; bone that the joint is attached to
		self.joint_to_bone = Array(self.context, 0, None, (0,), name_type_map['Int'])

		# the inverse of the above; for each bone info bone, index of the corresponding joint or -1 if no joint
		self.bone_to_joint = Array(self.context, 0, None, (0,), name_type_map['Int'])
		self.joint_names = name_type_map['ZStringBuffer'](self.context, self.namespace_length, None)
		self.joint_names_padding = name_type_map['PadAlign'](self.context, 8, self.names_ref)

		# this seems to be always multiples of 8 bytes
		# fails on PC SP_Scarecrow, because its first hitcheck has collision type 0
		# old, not sure what ms2: the padding goes wrong on 144
		self.after_names = name_type_map['AfterJointsPadding'](self.context, 8, None)

		# new style - includes name offset, some flags and the hitchecks
		self.joint_infos = Array(self.context, self.joint_names, None, (0,), name_type_map['JointInfo'])

		# old style - for each joint, read the hitchecks
		self.hitcheck_reader = name_type_map['HitcheckReader'](self.context, self, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'start_pc', name_type_map['SmartPadding'], (0, None), (False, None), (lambda context: context.version == 32, None)
		yield 'before_dla_0', name_type_map['Uint64'], (0, None), (False, None), (lambda context: context.version <= 7, None)
		yield 'before_dla_1', name_type_map['Uint64'], (0, None), (False, None), (lambda context: context.version <= 7, None)
		yield 'joint_count', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'num_push_constraints', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'num_stretch_constraints', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'num_ragdoll_constraints', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'zero_0', name_type_map['Uint'], (0, None), (False, None), (lambda context: context.version <= 32, None)
		yield 'zero_1', name_type_map['Uint'], (0, None), (False, None), (lambda context: 13 <= context.version <= 32, None)
		yield 'namespace_length', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'zeros_0', Array, (0, None, (5,), name_type_map['Uint']), (False, None), (None, None)
		yield 'pc_count', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'zeros_1', Array, (0, None, (7,), name_type_map['Uint']), (False, None), (None, None)
		yield 'extra_zeros_2', Array, (0, None, (4,), name_type_map['Uint']), (False, None), (lambda context: 13 <= context.version <= 32, None)
		yield 'one_0', name_type_map['Uint64'], (0, None), (False, 1), (lambda context: context.version >= 13, None)
		yield 'one_1', name_type_map['Uint64'], (0, None), (False, 1), (lambda context: context.version >= 13, None)
		yield 'bone_count', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'joint_entry_count', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'zeros_2', Array, (0, None, (4,), name_type_map['Uint']), (False, None), (None, None)
		yield 'zeros_3', name_type_map['Uint'], (0, None), (False, None), (lambda context: context.version <= 7, None)
		yield 'names_ref', name_type_map['Empty'], (0, None), (False, None), (None, None)
		yield 'joint_transforms', Array, (0, None, (None,), name_type_map['JointTransform']), (False, None), (None, None)
		yield 'rigid_body_pointers', Array, (0, None, (None,), name_type_map['Uint64']), (False, None), (lambda context: context.version >= 47, None)
		yield 'rigid_body_list', Array, (0, None, (None,), name_type_map['RigidBody']), (False, None), (lambda context: context.version >= 47, None)
		yield 'push_constraints', Array, (0, None, (None,), name_type_map['PushConstraint']), (False, None), (lambda context: context.version >= 47, None)
		yield 'stretch_constraints', Array, (0, None, (None,), name_type_map['StretchConstraint']), (False, None), (lambda context: context.version >= 47, None)
		yield 'ragdoll_constraints', Array, (0, None, (None,), name_type_map['RagdollConstraint']), (False, None), (lambda context: context.version >= 47, None)
		yield 'joint_infos', Array, (0, None, (None,), name_type_map['UACJointFF']), (False, None), (lambda context: context.version <= 32, None)
		yield 'pc_floats', Array, (0, None, (None, 10,), name_type_map['Float']), (False, None), (lambda context: context.version <= 32, None)
		yield 'names_ref_pc', name_type_map['Empty'], (0, None), (False, None), (None, None)
		yield 'joint_to_bone', Array, (0, None, (None,), name_type_map['Int']), (False, None), (None, None)
		yield 'bone_to_joint', Array, (0, None, (None,), name_type_map['Int']), (False, None), (None, None)
		yield 'joint_names', name_type_map['ZStringBuffer'], (None, None), (False, None), (None, None)
		yield 'joint_names_padding', name_type_map['PadAlign'], (8, None), (False, None), (None, None)
		yield 'after_names', name_type_map['AfterJointsPadding'], (8, None), (False, None), (lambda context: context.version <= 32, None)
		yield 'joint_infos', Array, (None, None, (None,), name_type_map['JointInfo']), (False, None), (lambda context: context.version >= 47, None)
		yield 'hitcheck_reader', name_type_map['HitcheckReader'], (None, None), (False, None), (lambda context: context.version <= 32, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		if instance.context.version == 32:
			yield 'start_pc', name_type_map['SmartPadding'], (0, None), (False, None)
		if instance.context.version <= 7:
			yield 'before_dla_0', name_type_map['Uint64'], (0, None), (False, None)
			yield 'before_dla_1', name_type_map['Uint64'], (0, None), (False, None)
		yield 'joint_count', name_type_map['Uint'], (0, None), (False, None)
		yield 'num_push_constraints', name_type_map['Uint'], (0, None), (False, None)
		yield 'num_stretch_constraints', name_type_map['Uint'], (0, None), (False, None)
		yield 'num_ragdoll_constraints', name_type_map['Uint'], (0, None), (False, None)
		if instance.context.version <= 32:
			yield 'zero_0', name_type_map['Uint'], (0, None), (False, None)
		if 13 <= instance.context.version <= 32:
			yield 'zero_1', name_type_map['Uint'], (0, None), (False, None)
		yield 'namespace_length', name_type_map['Uint'], (0, None), (False, None)
		yield 'zeros_0', Array, (0, None, (5,), name_type_map['Uint']), (False, None)
		yield 'pc_count', name_type_map['Uint'], (0, None), (False, None)
		yield 'zeros_1', Array, (0, None, (7,), name_type_map['Uint']), (False, None)
		if 13 <= instance.context.version <= 32:
			yield 'extra_zeros_2', Array, (0, None, (4,), name_type_map['Uint']), (False, None)
		if instance.context.version >= 13:
			yield 'one_0', name_type_map['Uint64'], (0, None), (False, 1)
			yield 'one_1', name_type_map['Uint64'], (0, None), (False, 1)
		yield 'bone_count', name_type_map['Uint'], (0, None), (False, None)
		yield 'joint_entry_count', name_type_map['Uint'], (0, None), (False, None)
		yield 'zeros_2', Array, (0, None, (4,), name_type_map['Uint']), (False, None)
		if instance.context.version <= 7:
			yield 'zeros_3', name_type_map['Uint'], (0, None), (False, None)
		yield 'names_ref', name_type_map['Empty'], (0, None), (False, None)
		yield 'joint_transforms', Array, (0, None, (instance.joint_count,), name_type_map['JointTransform']), (False, None)
		if instance.context.version >= 47:
			yield 'rigid_body_pointers', Array, (0, None, (instance.joint_count,), name_type_map['Uint64']), (False, None)
			yield 'rigid_body_list', Array, (0, None, (instance.joint_count,), name_type_map['RigidBody']), (False, None)
			yield 'push_constraints', Array, (0, None, (instance.num_push_constraints,), name_type_map['PushConstraint']), (False, None)
			yield 'stretch_constraints', Array, (0, None, (instance.num_stretch_constraints,), name_type_map['StretchConstraint']), (False, None)
			yield 'ragdoll_constraints', Array, (0, None, (instance.num_ragdoll_constraints,), name_type_map['RagdollConstraint']), (False, None)
		if instance.context.version <= 32:
			yield 'joint_infos', Array, (0, None, (instance.joint_count,), name_type_map['UACJointFF']), (False, None)
			yield 'pc_floats', Array, (0, None, (instance.pc_count, 10,), name_type_map['Float']), (False, None)
		yield 'names_ref_pc', name_type_map['Empty'], (0, None), (False, None)
		yield 'joint_to_bone', Array, (0, None, (instance.joint_count,), name_type_map['Int']), (False, None)
		yield 'bone_to_joint', Array, (0, None, (instance.bone_count,), name_type_map['Int']), (False, None)
		yield 'joint_names', name_type_map['ZStringBuffer'], (instance.namespace_length, None), (False, None)
		yield 'joint_names_padding', name_type_map['PadAlign'], (8, instance.names_ref), (False, None)
		if instance.context.version <= 32:
			yield 'after_names', name_type_map['AfterJointsPadding'], (8, None), (False, None)
		if instance.context.version >= 47:
			yield 'joint_infos', Array, (instance.joint_names, None, (instance.joint_count,), name_type_map['JointInfo']), (False, None)
		if instance.context.version <= 32:
			yield 'hitcheck_reader', name_type_map['HitcheckReader'], (instance, None), (False, None)

	def get_strings(self):
		"""Get all strings in the structure."""
		condition_function = lambda x: issubclass(x[1], OffsetString)
		for val in self.get_condition_values_recursive(self, condition_function):
			yield val

	def get_pointers(self):
		"""Get all strings in the structure."""
		condition_function = lambda x: issubclass(x[1], JointPointer)
		for val in self.get_condition_values_recursive(self, condition_function):
			yield val

	def get_string_attribs(self):
		"""Get all strings in the structure."""
		condition_function = lambda x: issubclass(x[1], OffsetString)
		for s_type, s_inst, (f_name, f_type, arguments, _) in self.get_condition_attributes_recursive(self, self, condition_function):
			yield s_inst, f_name

	@classmethod
	def read_fields(cls, stream, instance):
		super().read_fields(stream, instance)
		# after reading, we can resolve the joint pointers
		for ptr in instance.get_pointers():
			ptr.joint = instance.joint_infos[ptr.index]
	# 	# after reading, resolve the names to string
	# 	for child_instance, attrib in instance.get_string_attribs():
	# 		# get the offset
	# 		offset = child_instance.get_field(child_instance, attrib)
	# 		# get str from ZStringBuffer
	# 		string = instance.joint_names.get_str_at(offset)
	# 		# set the string
	# 		cls.set_field(child_instance, attrib, string)

	@classmethod
	def write_fields(cls, stream, instance):
		strings = list(instance.get_strings())
		instance.joint_names.update_strings(strings)
		instance.namespace_length = len(instance.joint_names.data)
		# update indices of joint pointers
		joints_map = {j: i for i, j in enumerate(instance.joint_infos)}
		for ptr in instance.get_pointers():
			ptr.index = joints_map.get(ptr.joint)
		super().write_fields(stream, instance)


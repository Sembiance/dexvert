from nifgen.array import Array
from nifgen.base_struct import BaseStruct
from nifgen.formats.ms2.imports import name_type_map


class BoneInfo(BaseStruct):

	"""
	# 858 in DLA c_cl_thread_.ms2
	"""

	__name__ = 'BoneInfo'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.name_count = name_type_map['Uint'](self.context, 0, None)

		# ?
		self.z_0 = name_type_map['Ushort'](self.context, 0, None)
		self.inv_names_count = name_type_map['Ushort'](self.context, 0, None)
		self.bone_limits = Array(self.context, 0, None, (0,), name_type_map['BonePointer'])
		self.zero_0 = name_type_map['Short'].from_value(0)
		self.unknown_0_c = name_type_map['Uint'](self.context, 0, None)

		# almost always 4, 1 for male african lion
		self.unk_count = name_type_map['Uint'](self.context, 0, None)
		self.unk_unused = name_type_map['Uint'](self.context, 0, None)

		# ?
		self.war_a = name_type_map['Ushort'](self.context, 0, None)
		self.bone_limits = Array(self.context, 0, None, (0,), name_type_map['BonePointer'])

		# ?
		self.war_b = name_type_map['Ushort'](self.context, 0, None)
		self.bind_matrix_count = name_type_map['Uint64'](self.context, 0, None)
		self.zeros = Array(self.context, 0, None, (0,), name_type_map['Uint64'])
		self.inv_data_count = name_type_map['Uint64'](self.context, 0, None)
		self.bone_count = name_type_map['Uint64'](self.context, 0, None)
		self.unknown_40 = name_type_map['Uint64'](self.context, 0, None)
		self.parents_count = name_type_map['Uint64'](self.context, 0, None)

		# not PC, JWE
		self.extra_zero = name_type_map['Uint64'](self.context, 0, None)
		self.enum_count = name_type_map['Uint64'](self.context, 0, None)

		# usually zero
		self.unknown_58 = name_type_map['Uint64'](self.context, 0, None)

		# always 1
		self.one = name_type_map['Uint64'].from_value(1)

		# this counts the weird padding at the end, usually == bone count, 0 in PZ aardvark
		self.zeros_count = name_type_map['Uint64'](self.context, 0, None)

		# matches the other count on dino entertainer, but ik_count is not present
		self.unk_pc_count = name_type_map['Uint64'](self.context, 0, None)
		self.ik_count = name_type_map['Uint64'](self.context, 0, None)
		self.joint_count = name_type_map['Uint64'](self.context, 0, None)
		self.zero_1 = name_type_map['Uint64'].from_value(0)
		self.zero_2 = name_type_map['Uint64'].from_value(0)
		self.zero_3 = name_type_map['Uint64'].from_value(0)
		self.names_ref = name_type_map['Empty'](self.context, 0, None)
		self.name_indices = Array(self.context, 0, None, (0,), name_type_map['Uint'])
		self.inventory_name_indices = Array(self.context, 0, None, (0,), name_type_map['Ushort'])

		# align to 16 bytes
		self.name_padding = name_type_map['PadAlign'](self.context, 16, self.names_ref)

		# used for skinning
		self.inverse_bind_matrices = Array(self.context, 0, None, (0,), name_type_map['Matrix44'])
		self.bones = Array(self.context, 0, None, (0,), name_type_map['Bone'])

		# 255 = root, index in this list is the current bone index, value is the bone's parent index
		self.parents = Array(self.context, 0, None, (0,), name_type_map['Ushort'])

		# align to 8 bytes
		self.parents_padding = name_type_map['PadAlign'](self.context, 8, self.names_ref)

		# enumerates all bone indices, 4 may be flags

		# enumerates all bone indices
		self.enumeration = Array(self.context, 0, None, (0,), name_type_map['Ubyte'])

		# zeros
		self.inventory_datas = Array(self.context, 0, None, (0,), name_type_map['Byte'])

		# -1s and 0s

		# zeros
		self.weirdness = Array(self.context, 0, None, (0,), name_type_map['Short'])

		# zeros
		self.inventory_datas_2 = Array(self.context, 0, None, (0,), name_type_map['Int'])

		# weird -1s
		self.minus_padding = name_type_map['MinusPadding'](self.context, self.zeros_count, None)

		# weird zeros
		self.zeros_padding = name_type_map['ZerosPadding'](self.context, self.zeros_count, None)

		# IK Data
		self.ik_info = name_type_map['IKInfo'](self.context, self, None)

		# joints
		self.joints = name_type_map['JointData'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'name_count', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'z_0', name_type_map['Ushort'], (0, None), (False, None), (None, None)
		yield 'inv_names_count', name_type_map['Ushort'], (0, None), (False, None), (None, None)
		yield 'bone_limits', Array, (0, None, (2,), name_type_map['BonePointer']), (False, -1), (lambda context: 32 <= context.version <= 52, None)
		yield 'zero_0', name_type_map['Short'], (0, None), (False, 0), (lambda context: 32 <= context.version <= 52, None)
		yield 'unknown_0_c', name_type_map['Uint'], (0, None), (False, None), (lambda context: context.version >= 32, None)
		yield 'unk_count', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'unk_unused', name_type_map['Uint'], (0, None), (False, None), (lambda context: context.version <= 52, None)
		yield 'war_a', name_type_map['Ushort'], (0, None), (False, None), (lambda context: context.version >= 53, None)
		yield 'bone_limits', Array, (0, None, (2,), name_type_map['BonePointer']), (False, -1), (lambda context: context.version >= 53, None)
		yield 'war_b', name_type_map['Ushort'], (0, None), (False, None), (lambda context: context.version >= 53, None)
		yield 'bind_matrix_count', name_type_map['Uint64'], (0, None), (False, None), (None, None)
		yield 'zeros', Array, (0, None, (2,), name_type_map['Uint64']), (False, None), (None, None)
		yield 'inv_data_count', name_type_map['Uint64'], (0, None), (False, None), (None, None)
		yield 'bone_count', name_type_map['Uint64'], (0, None), (False, None), (None, None)
		yield 'unknown_40', name_type_map['Uint64'], (0, None), (False, None), (None, None)
		yield 'parents_count', name_type_map['Uint64'], (0, None), (False, None), (None, None)
		yield 'extra_zero', name_type_map['Uint64'], (0, None), (False, None), (lambda context: not ((context.version == 32) or ((context.version == 47) or (context.version == 39))), None)
		yield 'enum_count', name_type_map['Uint64'], (0, None), (False, None), (None, None)
		yield 'unknown_58', name_type_map['Uint64'], (0, None), (False, None), (None, None)
		yield 'one', name_type_map['Uint64'], (0, None), (False, 1), (None, None)
		yield 'zeros_count', name_type_map['Uint64'], (0, None), (False, None), (None, None)
		yield 'unk_pc_count', name_type_map['Uint64'], (0, None), (False, None), (lambda context: context.version == 32, None)
		yield 'ik_count', name_type_map['Uint64'], (0, None), (False, None), (None, None)
		yield 'joint_count', name_type_map['Uint64'], (0, None), (False, None), (None, None)
		yield 'zero_1', name_type_map['Uint64'], (0, None), (False, 0), (None, None)
		yield 'zero_2', name_type_map['Uint64'], (0, None), (False, 0), (lambda context: context.version <= 13, None)
		yield 'zero_3', name_type_map['Uint64'], (0, None), (False, 0), (lambda context: (context.version == 47) or (context.version == 39), None)
		yield 'names_ref', name_type_map['Empty'], (0, None), (False, None), (None, None)
		yield 'name_indices', Array, (0, None, (None,), name_type_map['Ushort']), (False, None), (lambda context: context.version <= 32, None)
		yield 'name_indices', Array, (0, None, (None,), name_type_map['Uint']), (False, None), (lambda context: context.version >= 47, None)
		yield 'inventory_name_indices', Array, (0, None, (None,), name_type_map['Ushort']), (False, None), (lambda context: context.version <= 32, None)
		yield 'name_padding', name_type_map['PadAlign'], (16, None), (False, None), (None, None)
		yield 'inverse_bind_matrices', Array, (0, None, (None,), name_type_map['Matrix44']), (False, None), (None, None)
		yield 'bones', Array, (0, None, (None,), name_type_map['Bone']), (False, None), (None, None)
		yield 'parents', Array, (0, None, (None,), name_type_map['Ubyte']), (False, None), (lambda context: context.version <= 52, None)
		yield 'parents', Array, (0, None, (None,), name_type_map['Ushort']), (False, None), (lambda context: context.version >= 53, None)
		yield 'parents_padding', name_type_map['PadAlign'], (8, None), (False, None), (lambda context: context.version >= 32, None)
		yield 'enumeration', Array, (0, None, (None, 2,), name_type_map['Uint']), (False, None), (lambda context: context.version >= 32, True)
		yield 'enumeration', Array, (0, None, (None,), name_type_map['Ubyte']), (False, None), (lambda context: context.version <= 13, True)
		yield 'inventory_datas', Array, (0, None, (None, 6,), name_type_map['Byte']), (False, None), (lambda context: context.version == 7, None)
		yield 'weirdness', Array, (0, None, (8,), name_type_map['Short']), (False, None), (lambda context: context.version == 7, None)
		yield 'weirdness', Array, (0, None, (10,), name_type_map['Short']), (False, None), (lambda context: context.version == 13, None)
		yield 'inventory_datas_2', Array, (0, None, (None, 2,), name_type_map['Int']), (False, None), (lambda context: context.version == 7, None)
		yield 'minus_padding', name_type_map['MinusPadding'], (None, None), (False, None), (lambda context: context.version <= 32, True)
		yield 'zeros_padding', name_type_map['ZerosPadding'], (None, None), (False, None), (lambda context: context.version >= 47, True)
		yield 'ik_info', name_type_map['IKInfo'], (None, None), (False, None), (None, True)
		yield 'joints', name_type_map['JointData'], (0, None), (False, None), (None, True)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'name_count', name_type_map['Uint'], (0, None), (False, None)
		yield 'z_0', name_type_map['Ushort'], (0, None), (False, None)
		yield 'inv_names_count', name_type_map['Ushort'], (0, None), (False, None)
		if 32 <= instance.context.version <= 52:
			yield 'bone_limits', Array, (0, None, (2,), name_type_map['BonePointer']), (False, -1)
			yield 'zero_0', name_type_map['Short'], (0, None), (False, 0)
		if instance.context.version >= 32:
			yield 'unknown_0_c', name_type_map['Uint'], (0, None), (False, None)
		yield 'unk_count', name_type_map['Uint'], (0, None), (False, None)
		if instance.context.version <= 52:
			yield 'unk_unused', name_type_map['Uint'], (0, None), (False, None)
		if instance.context.version >= 53:
			yield 'war_a', name_type_map['Ushort'], (0, None), (False, None)
			yield 'bone_limits', Array, (0, None, (2,), name_type_map['BonePointer']), (False, -1)
			yield 'war_b', name_type_map['Ushort'], (0, None), (False, None)
		yield 'bind_matrix_count', name_type_map['Uint64'], (0, None), (False, None)
		yield 'zeros', Array, (0, None, (2,), name_type_map['Uint64']), (False, None)
		yield 'inv_data_count', name_type_map['Uint64'], (0, None), (False, None)
		yield 'bone_count', name_type_map['Uint64'], (0, None), (False, None)
		yield 'unknown_40', name_type_map['Uint64'], (0, None), (False, None)
		yield 'parents_count', name_type_map['Uint64'], (0, None), (False, None)
		if not ((instance.context.version == 32) or ((instance.context.version == 47) or (instance.context.version == 39))):
			yield 'extra_zero', name_type_map['Uint64'], (0, None), (False, None)
		yield 'enum_count', name_type_map['Uint64'], (0, None), (False, None)
		yield 'unknown_58', name_type_map['Uint64'], (0, None), (False, None)
		yield 'one', name_type_map['Uint64'], (0, None), (False, 1)
		yield 'zeros_count', name_type_map['Uint64'], (0, None), (False, None)
		if instance.context.version == 32:
			yield 'unk_pc_count', name_type_map['Uint64'], (0, None), (False, None)
		yield 'ik_count', name_type_map['Uint64'], (0, None), (False, None)
		yield 'joint_count', name_type_map['Uint64'], (0, None), (False, None)
		yield 'zero_1', name_type_map['Uint64'], (0, None), (False, 0)
		if instance.context.version <= 13:
			yield 'zero_2', name_type_map['Uint64'], (0, None), (False, 0)
		if (instance.context.version == 47) or (instance.context.version == 39):
			yield 'zero_3', name_type_map['Uint64'], (0, None), (False, 0)
		yield 'names_ref', name_type_map['Empty'], (0, None), (False, None)
		if instance.context.version <= 32:
			yield 'name_indices', Array, (0, None, (instance.name_count,), name_type_map['Ushort']), (False, None)
		if instance.context.version >= 47:
			yield 'name_indices', Array, (0, None, (instance.name_count,), name_type_map['Uint']), (False, None)
		if instance.context.version <= 32:
			yield 'inventory_name_indices', Array, (0, None, (instance.inv_names_count,), name_type_map['Ushort']), (False, None)
		yield 'name_padding', name_type_map['PadAlign'], (16, instance.names_ref), (False, None)
		yield 'inverse_bind_matrices', Array, (0, None, (instance.bind_matrix_count,), name_type_map['Matrix44']), (False, None)
		yield 'bones', Array, (0, None, (instance.bone_count,), name_type_map['Bone']), (False, None)
		if instance.context.version <= 52:
			yield 'parents', Array, (0, None, (instance.parents_count,), name_type_map['Ubyte']), (False, None)
		if instance.context.version >= 53:
			yield 'parents', Array, (0, None, (instance.parents_count,), name_type_map['Ushort']), (False, None)
		if instance.context.version >= 32:
			yield 'parents_padding', name_type_map['PadAlign'], (8, instance.names_ref), (False, None)
		if instance.context.version >= 32 and instance.one:
			yield 'enumeration', Array, (0, None, (instance.enum_count, 2,), name_type_map['Uint']), (False, None)
		if instance.context.version <= 13 and instance.one:
			yield 'enumeration', Array, (0, None, (instance.enum_count,), name_type_map['Ubyte']), (False, None)
		if instance.context.version == 7:
			yield 'inventory_datas', Array, (0, None, (instance.inv_data_count, 6,), name_type_map['Byte']), (False, None)
			yield 'weirdness', Array, (0, None, (8,), name_type_map['Short']), (False, None)
		if instance.context.version == 13:
			yield 'weirdness', Array, (0, None, (10,), name_type_map['Short']), (False, None)
		if instance.context.version == 7:
			yield 'inventory_datas_2', Array, (0, None, (instance.inv_data_count, 2,), name_type_map['Int']), (False, None)
		if instance.context.version <= 32 and instance.zeros_count:
			yield 'minus_padding', name_type_map['MinusPadding'], (instance.zeros_count, None), (False, None)
		if instance.context.version >= 47 and instance.zeros_count:
			yield 'zeros_padding', name_type_map['ZerosPadding'], (instance.zeros_count, None), (False, None)
		if instance.ik_count:
			yield 'ik_info', name_type_map['IKInfo'], (instance, None), (False, None)
		if instance.joint_count:
			yield 'joints', name_type_map['JointData'], (0, None), (False, None)

from nifgen.array import Array
from nifgen.base_struct import BaseStruct
from nifgen.formats.manis.imports import name_type_map


class ManiInfo(BaseStruct):

	"""
	288 bytes for JWE / PZ
	304 bytes for PC, ZTUAC (however the last 2 bytes are alignment, and not on the last member of the array)
	320 bytes for war
	"""

	__name__ = 'ManiInfo'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.ref = name_type_map['Empty'](self.context, 0, None)
		self.duration = name_type_map['Float'](self.context, 0, None)
		self.frame_count = name_type_map['Uint'](self.context, 0, None)

		# determines the format of keys data; apparently 4, 5, and 6 are the same
		self.dtype = name_type_map['ManisDtype'](self.context, 0, None)
		self.zeros_0 = Array(self.context, 0, None, (0,), name_type_map['Uint'])
		self.extra_pc_1 = name_type_map['Ushort'](self.context, 0, None)
		self.pos_bone_count = name_type_map['Ushort'](self.context, 0, None)
		self.ori_bone_count = name_type_map['Ushort'](self.context, 0, None)
		self.scl_bone_count = name_type_map['Ushort'](self.context, 0, None)
		self.unk_count_0 = name_type_map['Ushort'](self.context, 0, None)
		self.unk_count_1 = name_type_map['Ushort'](self.context, 0, None)
		self.unk_count_2 = name_type_map['Ushort'](self.context, 0, None)
		self.float_count = name_type_map['Ushort'](self.context, 0, None)
		self.pos_bone_count_repeat = name_type_map['Ushort'](self.context, 0, None)
		self.ori_bone_count_repeat = name_type_map['Ushort'](self.context, 0, None)
		self.scl_bone_count_repeat = name_type_map['Ushort'](self.context, 0, None)
		self.unk_0 = name_type_map['Ushort'](self.context, 0, None)
		self.unk_1 = name_type_map['Ushort'](self.context, 0, None)
		self.root_pos_bone = name_type_map['BoneIndex'].from_value(255)
		self.root_ori_bone = name_type_map['BoneIndex'].from_value(255)

		# can include joints, such as in PZ water wheel count 5 vs ms2 2 bones, plus joints
		self.target_bone_count = name_type_map['Uint64'](self.context, 0, None)
		self.pad_1 = name_type_map['PadAlign'](self.context, 16, self.ref)

		# 224 bytes
		self.zeros_2 = Array(self.context, 0, None, (0,), name_type_map['Uint64'])

		# 12 bytes
		self.extra_zeros_pc = Array(self.context, 0, None, (0,), name_type_map['Uint'])
		self.pos_bone_min = name_type_map['BoneIndex'](self.context, self.dtype, None)
		self.pos_bone_max = name_type_map['BoneIndex'](self.context, self.dtype, None)
		self.ori_bone_min = name_type_map['BoneIndex'](self.context, self.dtype, None)
		self.ori_bone_max = name_type_map['BoneIndex'](self.context, self.dtype, None)
		self.scl_bone_min = name_type_map['BoneIndex'](self.context, self.dtype, None)
		self.scl_bone_max = name_type_map['BoneIndex'](self.context, self.dtype, None)
		self.pos_bone_count_related = name_type_map['BoneIndex'](self.context, self.dtype, None)
		self.pos_bone_count_repeat = name_type_map['BoneIndex'](self.context, self.dtype, None)
		self.ori_bone_count_related = name_type_map['BoneIndex'](self.context, self.dtype, None)
		self.ori_bone_count_repeat = name_type_map['BoneIndex'](self.context, self.dtype, None)
		self.scl_bone_count_related = name_type_map['BoneIndex'](self.context, self.dtype, None)
		self.scl_bone_count_repeat = name_type_map['BoneIndex'](self.context, self.dtype, None)
		self.zero_0_end = name_type_map['Ushort'](self.context, 0, None)
		self.zero_1_end = name_type_map['Ushort'](self.context, 0, None)
		self.pad_2 = name_type_map['PadAlign'](self.context, 16, self.ref)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'ref', name_type_map['Empty'], (0, None), (False, None), (None, None)
		yield 'duration', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'frame_count', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'dtype', name_type_map['ManisDtype'], (0, None), (False, None), (None, None)
		yield 'zeros_0', Array, (0, None, (3,), name_type_map['Uint']), (False, None), (None, None)
		yield 'extra_pc_1', name_type_map['Ushort'], (0, None), (False, None), (lambda context: context.version <= 257, None)
		yield 'pos_bone_count', name_type_map['Ushort'], (0, None), (False, None), (None, None)
		yield 'ori_bone_count', name_type_map['Ushort'], (0, None), (False, None), (None, None)
		yield 'scl_bone_count', name_type_map['Ushort'], (0, None), (False, None), (None, None)
		yield 'unk_count_0', name_type_map['Ushort'], (0, None), (False, None), (None, None)
		yield 'unk_count_1', name_type_map['Ushort'], (0, None), (False, None), (None, None)
		yield 'unk_count_2', name_type_map['Ushort'], (0, None), (False, None), (None, None)
		yield 'float_count', name_type_map['Ushort'], (0, None), (False, None), (None, None)
		yield 'pos_bone_count_repeat', name_type_map['Ushort'], (0, None), (False, None), (lambda context: context.version <= 257, None)
		yield 'ori_bone_count_repeat', name_type_map['Ushort'], (0, None), (False, None), (lambda context: context.version <= 257, None)
		yield 'scl_bone_count_repeat', name_type_map['Ushort'], (0, None), (False, None), (lambda context: context.version <= 257, None)
		yield 'unk_0', name_type_map['Ushort'], (0, None), (False, None), (lambda context: context.version <= 257, None)
		yield 'unk_1', name_type_map['Ushort'], (0, None), (False, None), (lambda context: context.version <= 257, None)
		yield 'root_pos_bone', name_type_map['BoneIndex'], (None, None), (False, 255), (None, None)
		yield 'root_ori_bone', name_type_map['BoneIndex'], (None, None), (False, 255), (None, None)
		yield 'target_bone_count', name_type_map['Uint64'], (0, None), (False, None), (None, None)
		yield 'pad_1', name_type_map['PadAlign'], (16, None), (False, None), (None, None)
		yield 'zeros_2', Array, (0, None, (28,), name_type_map['Uint64']), (False, None), (None, None)
		yield 'extra_zeros_pc', Array, (0, None, (3,), name_type_map['Uint']), (False, None), (lambda context: context.version <= 257, None)
		yield 'pos_bone_min', name_type_map['BoneIndex'], (None, None), (False, None), (None, None)
		yield 'pos_bone_max', name_type_map['BoneIndex'], (None, None), (False, None), (None, None)
		yield 'ori_bone_min', name_type_map['BoneIndex'], (None, None), (False, None), (None, None)
		yield 'ori_bone_max', name_type_map['BoneIndex'], (None, None), (False, None), (None, None)
		yield 'scl_bone_min', name_type_map['BoneIndex'], (None, None), (False, None), (None, None)
		yield 'scl_bone_max', name_type_map['BoneIndex'], (None, None), (False, None), (None, None)
		yield 'pos_bone_count_related', name_type_map['BoneIndex'], (None, None), (False, None), (lambda context: context.version >= 258, None)
		yield 'pos_bone_count_repeat', name_type_map['BoneIndex'], (None, None), (False, None), (lambda context: context.version >= 258, None)
		yield 'ori_bone_count_related', name_type_map['BoneIndex'], (None, None), (False, None), (lambda context: context.version >= 258, None)
		yield 'ori_bone_count_repeat', name_type_map['BoneIndex'], (None, None), (False, None), (lambda context: context.version >= 258, None)
		yield 'scl_bone_count_related', name_type_map['BoneIndex'], (None, None), (False, None), (lambda context: context.version >= 258, None)
		yield 'scl_bone_count_repeat', name_type_map['BoneIndex'], (None, None), (False, None), (lambda context: context.version >= 258, None)
		yield 'zero_0_end', name_type_map['Ushort'], (0, None), (False, None), (lambda context: context.version >= 258, None)
		yield 'zero_1_end', name_type_map['Ushort'], (0, None), (False, None), (None, None)
		yield 'pad_2', name_type_map['PadAlign'], (16, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'ref', name_type_map['Empty'], (0, None), (False, None)
		yield 'duration', name_type_map['Float'], (0, None), (False, None)
		yield 'frame_count', name_type_map['Uint'], (0, None), (False, None)
		yield 'dtype', name_type_map['ManisDtype'], (0, None), (False, None)
		yield 'zeros_0', Array, (0, None, (3,), name_type_map['Uint']), (False, None)
		if instance.context.version <= 257:
			yield 'extra_pc_1', name_type_map['Ushort'], (0, None), (False, None)
		yield 'pos_bone_count', name_type_map['Ushort'], (0, None), (False, None)
		yield 'ori_bone_count', name_type_map['Ushort'], (0, None), (False, None)
		yield 'scl_bone_count', name_type_map['Ushort'], (0, None), (False, None)
		yield 'unk_count_0', name_type_map['Ushort'], (0, None), (False, None)
		yield 'unk_count_1', name_type_map['Ushort'], (0, None), (False, None)
		yield 'unk_count_2', name_type_map['Ushort'], (0, None), (False, None)
		yield 'float_count', name_type_map['Ushort'], (0, None), (False, None)
		if instance.context.version <= 257:
			yield 'pos_bone_count_repeat', name_type_map['Ushort'], (0, None), (False, None)
			yield 'ori_bone_count_repeat', name_type_map['Ushort'], (0, None), (False, None)
			yield 'scl_bone_count_repeat', name_type_map['Ushort'], (0, None), (False, None)
			yield 'unk_0', name_type_map['Ushort'], (0, None), (False, None)
			yield 'unk_1', name_type_map['Ushort'], (0, None), (False, None)
		yield 'root_pos_bone', name_type_map['BoneIndex'], (instance.dtype, None), (False, 255)
		yield 'root_ori_bone', name_type_map['BoneIndex'], (instance.dtype, None), (False, 255)
		yield 'target_bone_count', name_type_map['Uint64'], (0, None), (False, None)
		yield 'pad_1', name_type_map['PadAlign'], (16, instance.ref), (False, None)
		yield 'zeros_2', Array, (0, None, (28,), name_type_map['Uint64']), (False, None)
		if instance.context.version <= 257:
			yield 'extra_zeros_pc', Array, (0, None, (3,), name_type_map['Uint']), (False, None)
		yield 'pos_bone_min', name_type_map['BoneIndex'], (instance.dtype, None), (False, None)
		yield 'pos_bone_max', name_type_map['BoneIndex'], (instance.dtype, None), (False, None)
		yield 'ori_bone_min', name_type_map['BoneIndex'], (instance.dtype, None), (False, None)
		yield 'ori_bone_max', name_type_map['BoneIndex'], (instance.dtype, None), (False, None)
		yield 'scl_bone_min', name_type_map['BoneIndex'], (instance.dtype, None), (False, None)
		yield 'scl_bone_max', name_type_map['BoneIndex'], (instance.dtype, None), (False, None)
		if instance.context.version >= 258:
			yield 'pos_bone_count_related', name_type_map['BoneIndex'], (instance.dtype, None), (False, None)
			yield 'pos_bone_count_repeat', name_type_map['BoneIndex'], (instance.dtype, None), (False, None)
			yield 'ori_bone_count_related', name_type_map['BoneIndex'], (instance.dtype, None), (False, None)
			yield 'ori_bone_count_repeat', name_type_map['BoneIndex'], (instance.dtype, None), (False, None)
			yield 'scl_bone_count_related', name_type_map['BoneIndex'], (instance.dtype, None), (False, None)
			yield 'scl_bone_count_repeat', name_type_map['BoneIndex'], (instance.dtype, None), (False, None)
			yield 'zero_0_end', name_type_map['Ushort'], (0, None), (False, None)
		yield 'zero_1_end', name_type_map['Ushort'], (0, None), (False, None)
		yield 'pad_2', name_type_map['PadAlign'], (16, instance.ref), (False, None)

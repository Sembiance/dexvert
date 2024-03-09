from nifgen.array import Array
from nifgen.base_struct import BaseStruct
from nifgen.formats.manis.imports import name_type_map


class ManiBlock(BaseStruct):

	__name__ = 'ManiBlock'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.ref = name_type_map['Empty'](self.context, 0, None)
		self.pos_bones_names = Array(self.context, 0, None, (0,), name_type_map['ChannelName'])
		self.ori_bones_names = Array(self.context, 0, None, (0,), name_type_map['ChannelName'])
		self.scl_bones_names = Array(self.context, 0, None, (0,), name_type_map['ChannelName'])
		self.floats_names = Array(self.context, 0, None, (0,), name_type_map['ChannelName'])
		self.pos_channel_to_bone = Array(self.context, 0, None, (0,), self.template)
		self.ori_channel_to_bone = Array(self.context, 0, None, (0,), self.template)
		self.scl_channel_to_bone = Array(self.context, 0, None, (0,), self.template)
		self.pos_bone_to_channel = Array(self.context, 0, None, (0,), self.template)
		self.ori_bone_to_channel = Array(self.context, 0, None, (0,), self.template)
		self.scl_bone_to_channel = Array(self.context, 0, None, (0,), self.template)
		self.pad = name_type_map['PadAlign'](self.context, 4, self.ref)
		self.pos_bones = Array(self.context, 0, None, (0,), name_type_map['Vector3'])
		self.ori_bones = Array(self.context, 0, None, (0,), name_type_map['Vector4H'])
		self.shr_bones = Array(self.context, 0, None, (0,), name_type_map['Vector2'])
		self.scl_bones = Array(self.context, 0, None, (0,), name_type_map['Vector3'])
		self.floats = Array(self.context, 0, None, (0,), name_type_map['Float'])
		self.uncompressed_pad = name_type_map['PadAlign'](self.context, 16, self.ref)
		self.extra_war = name_type_map['WarExtra'](self.context, self, None)
		self.compressed = name_type_map['CompressedManiData'](self.context, self, None)
		self.subchunks = name_type_map['UnkChunkList'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'ref', name_type_map['Empty'], (0, None), (False, None), (None, None)
		yield 'pos_bones_names', Array, (0, None, (None,), name_type_map['ChannelName']), (False, None), (None, None)
		yield 'ori_bones_names', Array, (0, None, (None,), name_type_map['ChannelName']), (False, None), (None, None)
		yield 'scl_bones_names', Array, (0, None, (None,), name_type_map['ChannelName']), (False, None), (None, None)
		yield 'floats_names', Array, (0, None, (None,), name_type_map['ChannelName']), (False, None), (None, None)
		yield 'pos_channel_to_bone', Array, (0, None, (None,), None), (False, None), (None, None)
		yield 'ori_channel_to_bone', Array, (0, None, (None,), None), (False, None), (None, None)
		yield 'scl_channel_to_bone', Array, (0, None, (None,), None), (False, None), (None, None)
		yield 'pos_bone_to_channel', Array, (0, None, (None,), None), (False, None), (None, True)
		yield 'ori_bone_to_channel', Array, (0, None, (None,), None), (False, None), (None, True)
		yield 'scl_bone_to_channel', Array, (0, None, (None,), None), (False, None), (None, True)
		yield 'pad', name_type_map['PadAlign'], (4, None), (False, None), (None, None)
		yield 'pos_bones', Array, (0, None, (None, None,), name_type_map['Vector3']), (False, None), (None, True)
		yield 'ori_bones', Array, (0, None, (None, None,), name_type_map['Vector4H']), (False, None), (None, True)
		yield 'shr_bones', Array, (0, None, (None, None,), name_type_map['Vector2']), (False, None), (None, True)
		yield 'scl_bones', Array, (0, None, (None, None,), name_type_map['Vector3']), (False, None), (None, True)
		yield 'floats', Array, (0, None, (None, None,), name_type_map['Float']), (False, None), (None, None)
		yield 'uncompressed_pad', name_type_map['PadAlign'], (16, None), (False, None), (None, None)
		yield 'extra_war', name_type_map['WarExtra'], (None, None), (False, None), (None, True)
		yield 'compressed', name_type_map['CompressedManiData'], (None, None), (False, None), (None, True)
		yield 'subchunks', name_type_map['UnkChunkList'], (0, None), (False, None), (None, True)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'ref', name_type_map['Empty'], (0, None), (False, None)
		yield 'pos_bones_names', Array, (0, None, (instance.arg.pos_bone_count,), name_type_map['ChannelName']), (False, None)
		yield 'ori_bones_names', Array, (0, None, (instance.arg.ori_bone_count,), name_type_map['ChannelName']), (False, None)
		yield 'scl_bones_names', Array, (0, None, (instance.arg.scl_bone_count,), name_type_map['ChannelName']), (False, None)
		yield 'floats_names', Array, (0, None, (instance.arg.float_count,), name_type_map['ChannelName']), (False, None)
		yield 'pos_channel_to_bone', Array, (0, None, (instance.arg.pos_bone_count,), instance.template), (False, None)
		yield 'ori_channel_to_bone', Array, (0, None, (instance.arg.ori_bone_count,), instance.template), (False, None)
		yield 'scl_channel_to_bone', Array, (0, None, (instance.arg.scl_bone_count,), instance.template), (False, None)
		if instance.arg.pos_bone_min <= instance.arg.pos_bone_max:
			yield 'pos_bone_to_channel', Array, (0, None, ((instance.arg.pos_bone_max - instance.arg.pos_bone_min) + 1,), instance.template), (False, None)
		if instance.arg.ori_bone_min <= instance.arg.ori_bone_max:
			yield 'ori_bone_to_channel', Array, (0, None, ((instance.arg.ori_bone_max - instance.arg.ori_bone_min) + 1,), instance.template), (False, None)
		if instance.arg.scl_bone_min <= instance.arg.scl_bone_max:
			yield 'scl_bone_to_channel', Array, (0, None, ((instance.arg.scl_bone_max - instance.arg.scl_bone_min) + 1,), instance.template), (False, None)
		yield 'pad', name_type_map['PadAlign'], (4, instance.ref), (False, None)
		if instance.arg.dtype.compression == 0:
			yield 'pos_bones', Array, (0, None, (instance.arg.frame_count, instance.arg.pos_bone_count,), name_type_map['Vector3']), (False, None)
			yield 'ori_bones', Array, (0, None, (instance.arg.frame_count, instance.arg.ori_bone_count,), name_type_map['Vector4H']), (False, None)
			yield 'shr_bones', Array, (0, None, (instance.arg.frame_count, instance.arg.scl_bone_count,), name_type_map['Vector2']), (False, None)
			yield 'scl_bones', Array, (0, None, (instance.arg.frame_count, instance.arg.scl_bone_count,), name_type_map['Vector3']), (False, None)
		yield 'floats', Array, (0, None, (instance.arg.frame_count, instance.arg.float_count,), name_type_map['Float']), (False, None)
		yield 'uncompressed_pad', name_type_map['PadAlign'], (16, instance.ref), (False, None)
		if instance.arg.dtype.use_ushort == 1:
			yield 'extra_war', name_type_map['WarExtra'], (instance, None), (False, None)
		if instance.arg.dtype.compression > 0:
			yield 'compressed', name_type_map['CompressedManiData'], (instance, None), (False, None)
		if instance.arg.dtype.has_list > 0:
			yield 'subchunks', name_type_map['UnkChunkList'], (0, None), (False, None)

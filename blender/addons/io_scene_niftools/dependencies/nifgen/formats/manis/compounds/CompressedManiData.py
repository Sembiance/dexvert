from nifgen.array import Array
from nifgen.base_struct import BaseStruct
from nifgen.formats.manis.imports import name_type_map


class CompressedManiData(BaseStruct):

	__name__ = 'CompressedManiData'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.frame_count = name_type_map['Uint'](self.context, 0, None)
		self.ori_bone_count = name_type_map['Uint'](self.context, 0, None)
		self.pos_bone_count = name_type_map['Uint'](self.context, 0, None)
		self.scl_bone_count = name_type_map['Ushort'](self.context, 0, None)
		self.morph_bone_count = name_type_map['Ushort'](self.context, 0, None)

		# fixed 32 bytes
		self.zeros_18 = Array(self.context, 0, None, (0,), name_type_map['Uint'])
		self.name_a = name_type_map['String32'](self.context, 0, None)
		self.scale_min = name_type_map['Vector3'](self.context, 0, None)
		self.scale_max = name_type_map['Vector3'](self.context, 0, None)
		self.ptr_first_segment = name_type_map['Uint64'](self.context, 0, None)
		self.unk_1 = name_type_map['Uint'](self.context, 0, None)
		self.unk_2 = name_type_map['Uint'](self.context, 0, None)

		# counts temporal segments
		self.segment_count = name_type_map['Ushort'](self.context, 0, None)

		# usually 420 or 52905
		self.quantisation_level = name_type_map['Ushort'](self.context, 0, None)
		self.unk_1 = name_type_map['Uint'](self.context, 0, None)
		self.unk_2 = name_type_map['Uint'](self.context, 0, None)
		self.ref_2 = name_type_map['Empty'](self.context, 0, None)

		# ?
		self.unk_3 = name_type_map['Uint'](self.context, 0, None)
		self.loc_bound_indices = Array(self.context, 0, None, (0,), name_type_map['Ubyte'])
		self.anoth_pad = name_type_map['PadAlign'](self.context, 4, self.ref_2)

		# not sure
		self.loc_bounds = name_type_map['FloatsGrabber'](self.context, self.loc_bound_indices, None)
		self.anoth_pad_2 = name_type_map['PadAlign'](self.context, 16, self.arg.ref)

		# give the byte size of the various temporal segments
		self.segments = Array(self.context, 0, None, (0,), name_type_map['Segment'])
		self.segments_data = name_type_map['SegmentsReader'](self.context, self.segments, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'frame_count', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'ori_bone_count', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'pos_bone_count', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'scl_bone_count', name_type_map['Ushort'], (0, None), (False, None), (None, None)
		yield 'morph_bone_count', name_type_map['Ushort'], (0, None), (False, None), (None, None)
		yield 'zeros_18', Array, (0, None, (8,), name_type_map['Uint']), (False, None), (lambda context: context.version >= 257, None)
		yield 'name_a', name_type_map['String32'], (0, None), (False, None), (lambda context: context.version <= 256, None)
		yield 'scale_min', name_type_map['Vector3'], (0, None), (False, None), (None, None)
		yield 'scale_max', name_type_map['Vector3'], (0, None), (False, None), (None, None)
		yield 'ptr_first_segment', name_type_map['Uint64'], (0, None), (False, None), (None, None)
		yield 'unk_1', name_type_map['Uint'], (0, None), (False, None), (lambda context: context.version >= 257, None)
		yield 'unk_2', name_type_map['Uint'], (0, None), (False, None), (lambda context: context.version >= 257, None)
		yield 'segment_count', name_type_map['Ushort'], (0, None), (False, None), (None, None)
		yield 'quantisation_level', name_type_map['Ushort'], (0, None), (False, None), (None, None)
		yield 'unk_1', name_type_map['Uint'], (0, None), (False, None), (lambda context: context.version <= 256, None)
		yield 'unk_2', name_type_map['Uint'], (0, None), (False, None), (lambda context: context.version <= 256, None)
		yield 'ref_2', name_type_map['Empty'], (0, None), (False, None), (None, None)
		yield 'unk_3', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'loc_bound_indices', Array, (0, None, (None,), name_type_map['Ubyte']), (False, None), (None, None)
		yield 'anoth_pad', name_type_map['PadAlign'], (4, None), (False, None), (None, None)
		yield 'loc_bounds', name_type_map['FloatsGrabber'], (None, None), (False, None), (None, None)
		yield 'anoth_pad_2', name_type_map['PadAlign'], (16, None), (False, None), (None, None)
		yield 'segments', Array, (0, None, (None,), name_type_map['Segment']), (False, None), (None, None)
		yield 'segments_data', name_type_map['SegmentsReader'], (None, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'frame_count', name_type_map['Uint'], (0, None), (False, None)
		yield 'ori_bone_count', name_type_map['Uint'], (0, None), (False, None)
		yield 'pos_bone_count', name_type_map['Uint'], (0, None), (False, None)
		yield 'scl_bone_count', name_type_map['Ushort'], (0, None), (False, None)
		yield 'morph_bone_count', name_type_map['Ushort'], (0, None), (False, None)
		if instance.context.version >= 257:
			yield 'zeros_18', Array, (0, None, (8,), name_type_map['Uint']), (False, None)
		if instance.context.version <= 256:
			yield 'name_a', name_type_map['String32'], (0, None), (False, None)
		yield 'scale_min', name_type_map['Vector3'], (0, None), (False, None)
		yield 'scale_max', name_type_map['Vector3'], (0, None), (False, None)
		yield 'ptr_first_segment', name_type_map['Uint64'], (0, None), (False, None)
		if instance.context.version >= 257:
			yield 'unk_1', name_type_map['Uint'], (0, None), (False, None)
			yield 'unk_2', name_type_map['Uint'], (0, None), (False, None)
		yield 'segment_count', name_type_map['Ushort'], (0, None), (False, None)
		yield 'quantisation_level', name_type_map['Ushort'], (0, None), (False, None)
		if instance.context.version <= 256:
			yield 'unk_1', name_type_map['Uint'], (0, None), (False, None)
			yield 'unk_2', name_type_map['Uint'], (0, None), (False, None)
		yield 'ref_2', name_type_map['Empty'], (0, None), (False, None)
		yield 'unk_3', name_type_map['Uint'], (0, None), (False, None)
		yield 'loc_bound_indices', Array, (0, None, (instance.pos_bone_count,), name_type_map['Ubyte']), (False, None)
		yield 'anoth_pad', name_type_map['PadAlign'], (4, instance.ref_2), (False, None)
		yield 'loc_bounds', name_type_map['FloatsGrabber'], (instance.loc_bound_indices, None), (False, None)
		yield 'anoth_pad_2', name_type_map['PadAlign'], (16, instance.arg.ref), (False, None)
		yield 'segments', Array, (0, None, (instance.segment_count,), name_type_map['Segment']), (False, None)
		yield 'segments_data', name_type_map['SegmentsReader'], (instance.segments, None), (False, None)

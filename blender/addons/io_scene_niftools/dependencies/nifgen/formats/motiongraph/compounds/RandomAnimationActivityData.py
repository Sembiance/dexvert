from nifgen.formats.motiongraph.imports import name_type_map
from nifgen.formats.ovl_base.compounds.MemStruct import MemStruct


class RandomAnimationActivityData(MemStruct):

	"""
	112 bytes
	"""

	__name__ = 'RandomAnimationActivityData'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.num_animations = name_type_map['Uint64'](self.context, 0, None)
		self.data_streams_count = name_type_map['Uint64'](self.context, 0, None)
		self.num_looped_animations = name_type_map['Uint64'](self.context, 0, None)
		self.looped_data_streams_count = name_type_map['Uint64'](self.context, 0, None)
		self.duration = name_type_map['Float'](self.context, 0, None)
		self.blend_time = name_type_map['Float'](self.context, 0, None)
		self.min_weight = name_type_map['Float'](self.context, 0, None)
		self.max_weight = name_type_map['Float'](self.context, 0, None)
		self.min_gap = name_type_map['Float'](self.context, 0, None)
		self.max_gap = name_type_map['Float'](self.context, 0, None)
		self.priorities = name_type_map['Uint'](self.context, 0, None)
		self.random_animation_flags = name_type_map['Uint'](self.context, 0, None)
		self.animations = name_type_map['ArrayPointer'](self.context, self.num_animations, name_type_map['ActivityAnimationInfo'])
		self.data_streams = name_type_map['ArrayPointer'](self.context, self.data_streams_count, name_type_map['DataStreamResourceDataList'])
		self.looped_animations = name_type_map['ArrayPointer'](self.context, self.num_looped_animations, name_type_map['LoopedAnimationInfo'])
		self.looped_data_streams = name_type_map['ArrayPointer'](self.context, self.looped_data_streams_count, name_type_map['DataStreamResourceDataList'])
		self.sync_variable = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		self.random_number_variable = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'num_animations', name_type_map['Uint64'], (0, None), (False, None), (None, None)
		yield 'animations', name_type_map['ArrayPointer'], (None, name_type_map['ActivityAnimationInfo']), (False, None), (None, None)
		yield 'data_streams_count', name_type_map['Uint64'], (0, None), (False, None), (None, None)
		yield 'data_streams', name_type_map['ArrayPointer'], (None, name_type_map['DataStreamResourceDataList']), (False, None), (None, None)
		yield 'num_looped_animations', name_type_map['Uint64'], (0, None), (False, None), (None, None)
		yield 'looped_animations', name_type_map['ArrayPointer'], (None, name_type_map['LoopedAnimationInfo']), (False, None), (None, None)
		yield 'looped_data_streams_count', name_type_map['Uint64'], (0, None), (False, None), (None, None)
		yield 'looped_data_streams', name_type_map['ArrayPointer'], (None, name_type_map['DataStreamResourceDataList']), (False, None), (None, None)
		yield 'duration', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'blend_time', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'min_weight', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'max_weight', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'min_gap', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'max_gap', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'priorities', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'random_animation_flags', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'sync_variable', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'random_number_variable', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'num_animations', name_type_map['Uint64'], (0, None), (False, None)
		yield 'animations', name_type_map['ArrayPointer'], (instance.num_animations, name_type_map['ActivityAnimationInfo']), (False, None)
		yield 'data_streams_count', name_type_map['Uint64'], (0, None), (False, None)
		yield 'data_streams', name_type_map['ArrayPointer'], (instance.data_streams_count, name_type_map['DataStreamResourceDataList']), (False, None)
		yield 'num_looped_animations', name_type_map['Uint64'], (0, None), (False, None)
		yield 'looped_animations', name_type_map['ArrayPointer'], (instance.num_looped_animations, name_type_map['LoopedAnimationInfo']), (False, None)
		yield 'looped_data_streams_count', name_type_map['Uint64'], (0, None), (False, None)
		yield 'looped_data_streams', name_type_map['ArrayPointer'], (instance.looped_data_streams_count, name_type_map['DataStreamResourceDataList']), (False, None)
		yield 'duration', name_type_map['Float'], (0, None), (False, None)
		yield 'blend_time', name_type_map['Float'], (0, None), (False, None)
		yield 'min_weight', name_type_map['Float'], (0, None), (False, None)
		yield 'max_weight', name_type_map['Float'], (0, None), (False, None)
		yield 'min_gap', name_type_map['Float'], (0, None), (False, None)
		yield 'max_gap', name_type_map['Float'], (0, None), (False, None)
		yield 'priorities', name_type_map['Uint'], (0, None), (False, None)
		yield 'random_animation_flags', name_type_map['Uint'], (0, None), (False, None)
		yield 'sync_variable', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'random_number_variable', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)

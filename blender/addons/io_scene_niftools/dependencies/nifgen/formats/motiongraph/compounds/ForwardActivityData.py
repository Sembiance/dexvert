from nifgen.formats.motiongraph.imports import name_type_map
from nifgen.formats.ovl_base.compounds.MemStruct import MemStruct


class ForwardActivityData(MemStruct):

	"""
	? bytes
	"""

	__name__ = 'ForwardActivityData'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.straight_forward_data_streams = name_type_map['DataStreamResourceDataList'](self.context, 0, None)
		self.left_forward_data_streams = name_type_map['DataStreamResourceDataList'](self.context, 0, None)
		self.right_forward_data_streams = name_type_map['DataStreamResourceDataList'](self.context, 0, None)
		self.straight_spot_data_streams = name_type_map['DataStreamResourceDataList'](self.context, 0, None)
		self.forward_flags = name_type_map['Ubyte'](self.context, 0, None)
		self.suppress_resource_data_streams = name_type_map['Ubyte'](self.context, 0, None)
		self.priorities = name_type_map['Ushort'](self.context, 0, None)
		self.turn_radius = name_type_map['Float'](self.context, 0, None)
		self.turn_radius_value_type = name_type_map['UseValueType'](self.context, 0, None)
		self._pad_0 = name_type_map['Ushort'](self.context, 0, None)
		self.stride_length = name_type_map['Float'](self.context, 0, None)
		self.stride_length_value_type = name_type_map['UseValueType'](self.context, 0, None)
		self._pad_1 = name_type_map['Ushort'](self.context, 0, None)
		self.lead_out_time = name_type_map['Float'](self.context, 0, None)
		self.anticipation_distance = name_type_map['Float'](self.context, 0, None)
		self.unfused_cycles = name_type_map['Uint'](self.context, 0, None)
		self.cycle_count = name_type_map['Uint'](self.context, 0, None)
		self.repeat_count = name_type_map['Uint'](self.context, 0, None)
		self.min_cycles = name_type_map['Uint'](self.context, 0, None)
		self.playback_rate = name_type_map['Float'](self.context, 0, None)
		self.straight_forward_animation = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		self.left_forward_animation = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		self.right_forward_animation = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		self.straight_spot_animation = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		self.output_prop_through_variable = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		self.cycled_variable = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'straight_forward_animation', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'left_forward_animation', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'right_forward_animation', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'straight_spot_animation', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'output_prop_through_variable', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'cycled_variable', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'straight_forward_data_streams', name_type_map['DataStreamResourceDataList'], (0, None), (False, None), (None, None)
		yield 'left_forward_data_streams', name_type_map['DataStreamResourceDataList'], (0, None), (False, None), (None, None)
		yield 'right_forward_data_streams', name_type_map['DataStreamResourceDataList'], (0, None), (False, None), (None, None)
		yield 'straight_spot_data_streams', name_type_map['DataStreamResourceDataList'], (0, None), (False, None), (None, None)
		yield 'forward_flags', name_type_map['Ubyte'], (0, None), (False, None), (None, None)
		yield 'suppress_resource_data_streams', name_type_map['Ubyte'], (0, None), (False, None), (None, None)
		yield 'priorities', name_type_map['Ushort'], (0, None), (False, None), (None, None)
		yield 'turn_radius', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'turn_radius_value_type', name_type_map['UseValueType'], (0, None), (False, None), (None, None)
		yield '_pad_0', name_type_map['Ushort'], (0, None), (False, None), (None, None)
		yield 'stride_length', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'stride_length_value_type', name_type_map['UseValueType'], (0, None), (False, None), (None, None)
		yield '_pad_1', name_type_map['Ushort'], (0, None), (False, None), (None, None)
		yield 'lead_out_time', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'anticipation_distance', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'unfused_cycles', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'cycle_count', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'repeat_count', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'min_cycles', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'playback_rate', name_type_map['Float'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'straight_forward_animation', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'left_forward_animation', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'right_forward_animation', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'straight_spot_animation', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'output_prop_through_variable', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'cycled_variable', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'straight_forward_data_streams', name_type_map['DataStreamResourceDataList'], (0, None), (False, None)
		yield 'left_forward_data_streams', name_type_map['DataStreamResourceDataList'], (0, None), (False, None)
		yield 'right_forward_data_streams', name_type_map['DataStreamResourceDataList'], (0, None), (False, None)
		yield 'straight_spot_data_streams', name_type_map['DataStreamResourceDataList'], (0, None), (False, None)
		yield 'forward_flags', name_type_map['Ubyte'], (0, None), (False, None)
		yield 'suppress_resource_data_streams', name_type_map['Ubyte'], (0, None), (False, None)
		yield 'priorities', name_type_map['Ushort'], (0, None), (False, None)
		yield 'turn_radius', name_type_map['Float'], (0, None), (False, None)
		yield 'turn_radius_value_type', name_type_map['UseValueType'], (0, None), (False, None)
		yield '_pad_0', name_type_map['Ushort'], (0, None), (False, None)
		yield 'stride_length', name_type_map['Float'], (0, None), (False, None)
		yield 'stride_length_value_type', name_type_map['UseValueType'], (0, None), (False, None)
		yield '_pad_1', name_type_map['Ushort'], (0, None), (False, None)
		yield 'lead_out_time', name_type_map['Float'], (0, None), (False, None)
		yield 'anticipation_distance', name_type_map['Float'], (0, None), (False, None)
		yield 'unfused_cycles', name_type_map['Uint'], (0, None), (False, None)
		yield 'cycle_count', name_type_map['Uint'], (0, None), (False, None)
		yield 'repeat_count', name_type_map['Uint'], (0, None), (False, None)
		yield 'min_cycles', name_type_map['Uint'], (0, None), (False, None)
		yield 'playback_rate', name_type_map['Float'], (0, None), (False, None)

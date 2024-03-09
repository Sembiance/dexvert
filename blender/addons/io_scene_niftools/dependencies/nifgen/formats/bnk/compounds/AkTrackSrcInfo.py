from nifgen.base_struct import BaseStruct
from nifgen.formats.bnk.imports import name_type_map


class AkTrackSrcInfo(BaseStruct):

	__name__ = 'AkTrackSrcInfo'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.track_i_d = name_type_map['Uint'](self.context, 0, None)
		self.source_i_d = name_type_map['Uint'](self.context, 0, None)
		self.event_i_d = name_type_map['Uint'](self.context, 0, None)
		self.f_play_at = name_type_map['Double'](self.context, 0, None)
		self.f_begin_trim_offset = name_type_map['Double'](self.context, 0, None)
		self.f_end_trim_offset = name_type_map['Double'](self.context, 0, None)
		self.f_src_duration = name_type_map['Double'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'track_i_d', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'source_i_d', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'event_i_d', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'f_play_at', name_type_map['Double'], (0, None), (False, None), (None, None)
		yield 'f_begin_trim_offset', name_type_map['Double'], (0, None), (False, None), (None, None)
		yield 'f_end_trim_offset', name_type_map['Double'], (0, None), (False, None), (None, None)
		yield 'f_src_duration', name_type_map['Double'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'track_i_d', name_type_map['Uint'], (0, None), (False, None)
		yield 'source_i_d', name_type_map['Uint'], (0, None), (False, None)
		yield 'event_i_d', name_type_map['Uint'], (0, None), (False, None)
		yield 'f_play_at', name_type_map['Double'], (0, None), (False, None)
		yield 'f_begin_trim_offset', name_type_map['Double'], (0, None), (False, None)
		yield 'f_end_trim_offset', name_type_map['Double'], (0, None), (False, None)
		yield 'f_src_duration', name_type_map['Double'], (0, None), (False, None)

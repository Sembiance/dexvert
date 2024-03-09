from nifgen.array import Array
from nifgen.base_struct import BaseStruct
from nifgen.formats.bnk.imports import name_type_map


class MusicTrackInitialValues(BaseStruct):

	__name__ = 'MusicTrackInitialValues'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.u_flags = name_type_map['Ubyte'](self.context, 0, None)
		self.num_sources = name_type_map['Uint'](self.context, 0, None)
		self.p_source = Array(self.context, 0, None, (0,), name_type_map['AkBankSourceData'])
		self.num_playlist_item = name_type_map['Uint'](self.context, 0, None)
		self.p_playlist = Array(self.context, 0, None, (0,), name_type_map['AkTrackSrcInfo'])
		self.num_sub_track = name_type_map['Uint'](self.context, 0, None)
		self.num_clip_automation_item = name_type_map['Uint'](self.context, 0, None)
		self.p_items = Array(self.context, 0, None, (0,), name_type_map['Uint'])
		self.node_base_params = name_type_map['NodeBaseParams'](self.context, 0, None)
		self.e_track_type = name_type_map['Ubyte'](self.context, 0, None)
		self.i_look_ahead_time = name_type_map['Int'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'u_flags', name_type_map['Ubyte'], (0, None), (False, None), (None, None)
		yield 'num_sources', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'p_source', Array, (0, None, (None,), name_type_map['AkBankSourceData']), (False, None), (None, None)
		yield 'num_playlist_item', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'p_playlist', Array, (0, None, (None,), name_type_map['AkTrackSrcInfo']), (False, None), (None, None)
		yield 'num_sub_track', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'num_clip_automation_item', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'p_items', Array, (0, None, (None,), name_type_map['Uint']), (False, None), (None, None)
		yield 'node_base_params', name_type_map['NodeBaseParams'], (0, None), (False, None), (None, None)
		yield 'e_track_type', name_type_map['Ubyte'], (0, None), (False, None), (None, None)
		yield 'i_look_ahead_time', name_type_map['Int'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'u_flags', name_type_map['Ubyte'], (0, None), (False, None)
		yield 'num_sources', name_type_map['Uint'], (0, None), (False, None)
		yield 'p_source', Array, (0, None, (instance.num_sources,), name_type_map['AkBankSourceData']), (False, None)
		yield 'num_playlist_item', name_type_map['Uint'], (0, None), (False, None)
		yield 'p_playlist', Array, (0, None, (instance.num_playlist_item,), name_type_map['AkTrackSrcInfo']), (False, None)
		yield 'num_sub_track', name_type_map['Uint'], (0, None), (False, None)
		yield 'num_clip_automation_item', name_type_map['Uint'], (0, None), (False, None)
		yield 'p_items', Array, (0, None, (instance.num_clip_automation_item,), name_type_map['Uint']), (False, None)
		yield 'node_base_params', name_type_map['NodeBaseParams'], (0, None), (False, None)
		yield 'e_track_type', name_type_map['Ubyte'], (0, None), (False, None)
		yield 'i_look_ahead_time', name_type_map['Int'], (0, None), (False, None)

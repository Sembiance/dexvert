from nifgen.base_struct import BaseStruct
from nifgen.formats.bnk.imports import name_type_map


class MusicTrack(BaseStruct):

	__name__ = 'MusicTrack'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# seen 114
		self.length = name_type_map['Uint'](self.context, 0, None)
		self.id = name_type_map['Uint'](self.context, 0, None)
		self.data = name_type_map['MusicTrackInitialValues'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'length', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'id', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'data', name_type_map['MusicTrackInitialValues'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'length', name_type_map['Uint'], (0, None), (False, None)
		yield 'id', name_type_map['Uint'], (0, None), (False, None)
		yield 'data', name_type_map['MusicTrackInitialValues'], (0, None), (False, None)

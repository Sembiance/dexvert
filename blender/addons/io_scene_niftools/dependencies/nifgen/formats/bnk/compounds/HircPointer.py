from nifgen.base_struct import BaseStruct
from nifgen.formats.bnk.imports import name_type_map


class HircPointer(BaseStruct):

	__name__ = 'HircPointer'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.id = name_type_map['HircType'](self.context, 0, None)
		self.data = name_type_map['TypeOther'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'id', name_type_map['HircType'], (0, None), (False, None), (None, None)
		yield 'data', name_type_map['SoundSfxVoice'], (0, None), (False, None), (None, True)
		yield 'data', name_type_map['MusicTrack'], (0, None), (False, None), (None, True)
		yield 'data', name_type_map['TypeOther'], (0, None), (False, None), (None, True)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'id', name_type_map['HircType'], (0, None), (False, None)
		if instance.id == 2:
			yield 'data', name_type_map['SoundSfxVoice'], (0, None), (False, None)
		if instance.id == 11:
			yield 'data', name_type_map['MusicTrack'], (0, None), (False, None)
		if (instance.id != 2) and (instance.id != 11):
			yield 'data', name_type_map['TypeOther'], (0, None), (False, None)

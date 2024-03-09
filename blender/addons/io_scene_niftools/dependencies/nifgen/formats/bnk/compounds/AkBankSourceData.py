from nifgen.base_struct import BaseStruct
from nifgen.formats.bnk.imports import name_type_map


class AkBankSourceData(BaseStruct):

	__name__ = 'AkBankSourceData'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.ul_plugin_i_d = name_type_map['Uint'](self.context, 0, None)
		self.stream_type = name_type_map['Ubyte'](self.context, 0, None)
		self.ak_media_information = name_type_map['AkMediaInformation'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'ul_plugin_i_d', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'stream_type', name_type_map['Ubyte'], (0, None), (False, None), (None, None)
		yield 'ak_media_information', name_type_map['AkMediaInformation'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'ul_plugin_i_d', name_type_map['Uint'], (0, None), (False, None)
		yield 'stream_type', name_type_map['Ubyte'], (0, None), (False, None)
		yield 'ak_media_information', name_type_map['AkMediaInformation'], (0, None), (False, None)

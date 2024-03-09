from nifgen.formats.ovl_base.compounds.MemStruct import MemStruct
from nifgen.formats.scaleformlanguagedata.imports import name_type_map


class FontInfo(MemStruct):

	"""
	24 bytes
	"""

	__name__ = 'FontInfo'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.flag_or_count = name_type_map['Uint64'](self.context, 0, None)
		self.style_name = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		self.font_file = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'style_name', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'font_file', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'flag_or_count', name_type_map['Uint64'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'style_name', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'font_file', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'flag_or_count', name_type_map['Uint64'], (0, None), (False, None)

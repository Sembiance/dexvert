from nifgen.formats.ovl_base.compounds.MemStruct import MemStruct
from nifgen.formats.scaleformlanguagedata.imports import name_type_map


class ScaleformlanguagedataRoot(MemStruct):

	"""
	# PC - is maybe organized differently here
	PZ: 48 bytes
	"""

	__name__ = 'ScaleformlanguagedataRoot'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.zero_0 = name_type_map['Uint64'](self.context, 0, None)
		self.zero_1 = name_type_map['Uint64'](self.context, 0, None)
		self.count = name_type_map['Uint64'](self.context, 0, None)
		self.zero_2 = name_type_map['Uint64'](self.context, 0, None)
		self.zero_3 = name_type_map['Uint64'](self.context, 0, None)
		self.fonts = name_type_map['ArrayPointer'](self.context, self.count, name_type_map['FontInfo'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'zero_0', name_type_map['Uint64'], (0, None), (False, None), (None, None)
		yield 'zero_1', name_type_map['Uint64'], (0, None), (False, None), (None, None)
		yield 'fonts', name_type_map['ArrayPointer'], (None, name_type_map['FontInfo']), (False, None), (None, None)
		yield 'count', name_type_map['Uint64'], (0, None), (False, None), (None, None)
		yield 'zero_2', name_type_map['Uint64'], (0, None), (False, None), (None, None)
		yield 'zero_3', name_type_map['Uint64'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'zero_0', name_type_map['Uint64'], (0, None), (False, None)
		yield 'zero_1', name_type_map['Uint64'], (0, None), (False, None)
		yield 'fonts', name_type_map['ArrayPointer'], (instance.count, name_type_map['FontInfo']), (False, None)
		yield 'count', name_type_map['Uint64'], (0, None), (False, None)
		yield 'zero_2', name_type_map['Uint64'], (0, None), (False, None)
		yield 'zero_3', name_type_map['Uint64'], (0, None), (False, None)

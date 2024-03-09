from nifgen.formats.lut.imports import name_type_map
from nifgen.formats.ovl_base.compounds.MemStruct import MemStruct


class LutHeader(MemStruct):

	"""
	24 bytes for JWE2
	"""

	__name__ = 'LutHeader'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.colors_count = name_type_map['Ushort'](self.context, 0, None)
		self.unk_0 = name_type_map['Ushort'](self.context, 0, None)
		self.unk_1 = name_type_map['Uint'](self.context, 0, None)
		self.colors_in_column_count = name_type_map['Uint'](self.context, 0, None)
		self.unk_2 = name_type_map['Uint'](self.context, 0, None)
		self.colors = name_type_map['ArrayPointer'](self.context, self.colors_count, name_type_map['Vector3'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'colors', name_type_map['ArrayPointer'], (None, name_type_map['Vector3']), (False, None), (None, None)
		yield 'colors_count', name_type_map['Ushort'], (0, None), (False, None), (None, None)
		yield 'unk_0', name_type_map['Ushort'], (0, None), (False, None), (None, None)
		yield 'unk_1', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'colors_in_column_count', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'unk_2', name_type_map['Uint'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'colors', name_type_map['ArrayPointer'], (instance.colors_count, name_type_map['Vector3']), (False, None)
		yield 'colors_count', name_type_map['Ushort'], (0, None), (False, None)
		yield 'unk_0', name_type_map['Ushort'], (0, None), (False, None)
		yield 'unk_1', name_type_map['Uint'], (0, None), (False, None)
		yield 'colors_in_column_count', name_type_map['Uint'], (0, None), (False, None)
		yield 'unk_2', name_type_map['Uint'], (0, None), (False, None)

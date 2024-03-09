from nifgen.formats.ovl_base.compounds.MemStruct import MemStruct
from nifgen.formats.particleeffect.imports import name_type_map


class LastRow(MemStruct):

	__name__ = 'LastRow'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.unk_07 = name_type_map['Ushort'](self.context, 0, None)
		self.unk_08 = name_type_map['Ushort'](self.context, 0, None)
		self.unk_09 = name_type_map['Ushort'](self.context, 0, None)
		self.unk_10 = name_type_map['Ushort'](self.context, 0, None)
		self.unk_11 = name_type_map['Ushort'](self.context, 0, None)
		self.unk_12 = name_type_map['Ushort'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'unk_07', name_type_map['Ushort'], (0, None), (False, None), (None, None)
		yield 'unk_08', name_type_map['Ushort'], (0, None), (False, None), (None, None)
		yield 'unk_09', name_type_map['Ushort'], (0, None), (False, None), (None, None)
		yield 'unk_10', name_type_map['Ushort'], (0, None), (False, None), (None, None)
		yield 'unk_11', name_type_map['Ushort'], (0, None), (False, None), (None, None)
		yield 'unk_12', name_type_map['Ushort'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'unk_07', name_type_map['Ushort'], (0, None), (False, None)
		yield 'unk_08', name_type_map['Ushort'], (0, None), (False, None)
		yield 'unk_09', name_type_map['Ushort'], (0, None), (False, None)
		yield 'unk_10', name_type_map['Ushort'], (0, None), (False, None)
		yield 'unk_11', name_type_map['Ushort'], (0, None), (False, None)
		yield 'unk_12', name_type_map['Ushort'], (0, None), (False, None)

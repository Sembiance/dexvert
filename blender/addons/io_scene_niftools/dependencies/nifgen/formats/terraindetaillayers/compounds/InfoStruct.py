from nifgen.formats.ovl_base.compounds.MemStruct import MemStruct
from nifgen.formats.terraindetaillayers.imports import name_type_map


class InfoStruct(MemStruct):

	__name__ = 'InfoStruct'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.brush_count = name_type_map['Uint'](self.context, 0, None)
		self.brush_flags = name_type_map['Uint'](self.context, 0, None)
		self.scale = name_type_map['Float'](self.context, 0, None)
		self.unk_1 = name_type_map['Float'](self.context, 0, None)
		self.brush_list = name_type_map['ArrayPointer'](self.context, self.brush_count, name_type_map['BrushitemStruct'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'brush_list', name_type_map['ArrayPointer'], (None, name_type_map['BrushitemStruct']), (False, None), (None, None)
		yield 'brush_count', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'brush_flags', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'scale', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'unk_1', name_type_map['Float'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'brush_list', name_type_map['ArrayPointer'], (instance.brush_count, name_type_map['BrushitemStruct']), (False, None)
		yield 'brush_count', name_type_map['Uint'], (0, None), (False, None)
		yield 'brush_flags', name_type_map['Uint'], (0, None), (False, None)
		yield 'scale', name_type_map['Float'], (0, None), (False, None)
		yield 'unk_1', name_type_map['Float'], (0, None), (False, None)

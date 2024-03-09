from nifgen.formats.ovl_base.compounds.MemStruct import MemStruct
from nifgen.formats.terrainindexeddetaillayers.imports import name_type_map


class TerrainDetailsLayerItem(MemStruct):

	__name__ = 'TerrainDetailsLayerItem'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.info_count = name_type_map['Uint64'](self.context, 0, None)
		self.layer_name = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		self.info_list = name_type_map['ArrayPointer'](self.context, self.info_count, name_type_map['BrushitemStruct'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'layer_name', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'info_list', name_type_map['ArrayPointer'], (None, name_type_map['BrushitemStruct']), (False, None), (None, None)
		yield 'info_count', name_type_map['Uint64'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'layer_name', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'info_list', name_type_map['ArrayPointer'], (instance.info_count, name_type_map['BrushitemStruct']), (False, None)
		yield 'info_count', name_type_map['Uint64'], (0, None), (False, None)

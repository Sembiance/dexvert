from nifgen.formats.ovl_base.compounds.MemStruct import MemStruct
from nifgen.formats.terraindetaillayers.imports import name_type_map


class TerrainDetailLayersRoot(MemStruct):

	"""
	# 16 bytes
	"""

	__name__ = 'TerrainDetailLayersRoot'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.layer_count = name_type_map['Uint64'](self.context, 0, None)
		self.layer_list = name_type_map['ArrayPointer'](self.context, self.layer_count, name_type_map['TerrainDetailsLayerItem'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'layer_list', name_type_map['ArrayPointer'], (None, name_type_map['TerrainDetailsLayerItem']), (False, None), (None, None)
		yield 'layer_count', name_type_map['Uint64'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'layer_list', name_type_map['ArrayPointer'], (instance.layer_count, name_type_map['TerrainDetailsLayerItem']), (False, None)
		yield 'layer_count', name_type_map['Uint64'], (0, None), (False, None)

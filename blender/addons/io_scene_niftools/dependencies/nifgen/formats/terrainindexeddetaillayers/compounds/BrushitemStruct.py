from nifgen.formats.ovl_base.compounds.MemStruct import MemStruct
from nifgen.formats.terrainindexeddetaillayers.imports import name_type_map


class BrushitemStruct(MemStruct):

	__name__ = 'brushitemStruct'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.layer_name = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		self.brush_name = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'layer_name', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'brush_name', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'layer_name', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'brush_name', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)

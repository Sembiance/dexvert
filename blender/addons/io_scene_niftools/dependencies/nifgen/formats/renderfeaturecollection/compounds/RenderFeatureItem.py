from nifgen.formats.ovl_base.compounds.MemStruct import MemStruct
from nifgen.formats.renderfeaturecollection.imports import name_type_map


class RenderFeatureItem(MemStruct):

	__name__ = 'RenderFeatureItem'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.item_data_count = name_type_map['Uint64'](self.context, 0, None)
		self.item_name = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		self.item_data = name_type_map['ArrayPointer'](self.context, self.item_data_count, name_type_map['RenderFeatureSubItem'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'item_name', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'item_data', name_type_map['ArrayPointer'], (None, name_type_map['RenderFeatureSubItem']), (False, None), (None, None)
		yield 'item_data_count', name_type_map['Uint64'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'item_name', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'item_data', name_type_map['ArrayPointer'], (instance.item_data_count, name_type_map['RenderFeatureSubItem']), (False, None)
		yield 'item_data_count', name_type_map['Uint64'], (0, None), (False, None)

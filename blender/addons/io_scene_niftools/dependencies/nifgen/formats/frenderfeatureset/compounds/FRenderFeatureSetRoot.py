from nifgen.formats.frenderfeatureset.imports import name_type_map
from nifgen.formats.ovl_base.compounds.MemStruct import MemStruct


class FRenderFeatureSetRoot(MemStruct):

	__name__ = 'FRenderFeatureSetRoot'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.featureset_count = name_type_map['Uint'](self.context, 0, None)
		self.unknown_always_1 = name_type_map['Uint'](self.context, 0, None)
		self.featureset_list = name_type_map['ArrayPointer'](self.context, self.featureset_count, name_type_map['FeatureSetItem'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'featureset_list', name_type_map['ArrayPointer'], (None, name_type_map['FeatureSetItem']), (False, None), (None, None)
		yield 'featureset_count', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'unknown_always_1', name_type_map['Uint'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'featureset_list', name_type_map['ArrayPointer'], (instance.featureset_count, name_type_map['FeatureSetItem']), (False, None)
		yield 'featureset_count', name_type_map['Uint'], (0, None), (False, None)
		yield 'unknown_always_1', name_type_map['Uint'], (0, None), (False, None)

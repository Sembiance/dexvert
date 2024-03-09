from nifgen.formats.ovl_base.compounds.MemStruct import MemStruct
from nifgen.formats.path.imports import name_type_map


class PathMaterialData(MemStruct):

	__name__ = 'PathMaterialData'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.terrain_type = name_type_map['Uint'](self.context, 0, None)
		self.opacity = name_type_map['Float'](self.context, 0, None)
		self.padding = name_type_map['Uint64'].from_value(0)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'terrain_type', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'opacity', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'padding', name_type_map['Uint64'], (0, None), (True, 0), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'terrain_type', name_type_map['Uint'], (0, None), (False, None)
		yield 'opacity', name_type_map['Float'], (0, None), (False, None)
		yield 'padding', name_type_map['Uint64'], (0, None), (True, 0)

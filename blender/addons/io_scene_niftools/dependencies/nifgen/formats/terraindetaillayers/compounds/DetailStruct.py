from nifgen.formats.ovl_base.compounds.MemStruct import MemStruct
from nifgen.formats.terraindetaillayers.imports import name_type_map


class DetailStruct(MemStruct):

	__name__ = 'DetailStruct'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.index = name_type_map['Uint'](self.context, 0, None)
		self.x = name_type_map['Float'](self.context, 0, None)
		self.y = name_type_map['Float'](self.context, 0, None)
		self.z = name_type_map['Float'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'index', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'x', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'y', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'z', name_type_map['Float'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'index', name_type_map['Uint'], (0, None), (False, None)
		yield 'x', name_type_map['Float'], (0, None), (False, None)
		yield 'y', name_type_map['Float'], (0, None), (False, None)
		yield 'z', name_type_map['Float'], (0, None), (False, None)

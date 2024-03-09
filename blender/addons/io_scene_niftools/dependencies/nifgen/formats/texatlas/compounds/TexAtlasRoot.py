from nifgen.formats.ovl_base.compounds.MemStruct import MemStruct
from nifgen.formats.texatlas.imports import name_type_map


class TexAtlasRoot(MemStruct):

	__name__ = 'TexAtlasRoot'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.texture_count = name_type_map['Uint64'](self.context, 0, None)
		self.atlas_count = name_type_map['Uint64'](self.context, 0, None)
		self.texture_list = name_type_map['ArrayPointer'](self.context, self.texture_count, name_type_map['TextureData'])
		self.atlas_list = name_type_map['ArrayPointer'](self.context, self.atlas_count, name_type_map['AtlasItem'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'texture_list', name_type_map['ArrayPointer'], (None, name_type_map['TextureData']), (False, None), (None, None)
		yield 'texture_count', name_type_map['Uint64'], (0, None), (False, None), (None, None)
		yield 'atlas_list', name_type_map['ArrayPointer'], (None, name_type_map['AtlasItem']), (False, None), (None, None)
		yield 'atlas_count', name_type_map['Uint64'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'texture_list', name_type_map['ArrayPointer'], (instance.texture_count, name_type_map['TextureData']), (False, None)
		yield 'texture_count', name_type_map['Uint64'], (0, None), (False, None)
		yield 'atlas_list', name_type_map['ArrayPointer'], (instance.atlas_count, name_type_map['AtlasItem']), (False, None)
		yield 'atlas_count', name_type_map['Uint64'], (0, None), (False, None)

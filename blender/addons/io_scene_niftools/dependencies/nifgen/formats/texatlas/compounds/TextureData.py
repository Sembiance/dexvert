from nifgen.formats.ovl_base.compounds.MemStruct import MemStruct
from nifgen.formats.texatlas.imports import name_type_map


class TextureData(MemStruct):

	__name__ = 'TextureData'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.atlas_name = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])

		# texture
		self.dependency_name = name_type_map['Pointer'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'atlas_name', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'dependency_name', name_type_map['Pointer'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'atlas_name', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'dependency_name', name_type_map['Pointer'], (0, None), (False, None)

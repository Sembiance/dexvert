from nifgen.formats.fgm.imports import name_type_map
from nifgen.formats.ovl_base.compounds.MemStruct import MemStruct


class TextureData(MemStruct):

	__name__ = 'TextureData'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# only present if textured
		self.dependency_name = name_type_map['Pointer'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'dependency_name', name_type_map['Pointer'], (0, None), (False, None), (None, True)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		if instance.arg.dtype == 8:
			yield 'dependency_name', name_type_map['Pointer'], (0, None), (False, None)

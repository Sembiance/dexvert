from nifgen.formats.matcol.imports import name_type_map
from nifgen.formats.ovl_base.compounds.MemStruct import MemStruct


class Texture(MemStruct):

	__name__ = 'Texture'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# first fgm slot
		self.fgm_name = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		self.texture_suffix = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		self.texture_type = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'fgm_name', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'texture_suffix', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'texture_type', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'fgm_name', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'texture_suffix', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'texture_type', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)

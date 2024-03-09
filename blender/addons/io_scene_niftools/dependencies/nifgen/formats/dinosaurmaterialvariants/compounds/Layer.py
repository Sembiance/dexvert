from nifgen.formats.dinosaurmaterialvariants.imports import name_type_map
from nifgen.formats.ovl_base.compounds.MemStruct import MemStruct


class Layer(MemStruct):

	__name__ = 'Layer'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.has_ptr = name_type_map['Uint64'](self.context, 0, None)

		# defines the tiled texture material to be used
		self.texture_fgm_name = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])

		# defines how to transform the texture
		self.transform_fgm_name = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'has_ptr', name_type_map['Uint64'], (0, None), (False, None), (None, None)
		yield 'texture_fgm_name', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'transform_fgm_name', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'has_ptr', name_type_map['Uint64'], (0, None), (False, None)
		yield 'texture_fgm_name', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'transform_fgm_name', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)

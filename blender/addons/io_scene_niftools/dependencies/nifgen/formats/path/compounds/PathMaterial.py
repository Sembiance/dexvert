from nifgen.formats.ovl_base.compounds.MemStruct import MemStruct
from nifgen.formats.path.imports import name_type_map


class PathMaterial(MemStruct):

	__name__ = 'PathMaterial'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.path_sub_type = name_type_map['Uint64'](self.context, 0, None)
		self.num_data = name_type_map['Uint64'](self.context, 0, None)
		self.elevated_mat = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		self.elevated_mat_valid = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		self.elevated_mat_invalid = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		self.terrain_mat = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		self.terrain_mat_valid = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		self.terrain_mat_invalid = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		self.underside_mat_1 = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		self.underside_mat_2 = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		self.stairs_mat_1 = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		self.stairs_mat_2 = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		self.mat_data = name_type_map['ArrayPointer'](self.context, self.num_data, name_type_map['PathMaterialData'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'elevated_mat', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'elevated_mat_valid', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'elevated_mat_invalid', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'terrain_mat', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'terrain_mat_valid', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'terrain_mat_invalid', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'underside_mat_1', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'underside_mat_2', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'stairs_mat_1', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'stairs_mat_2', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'path_sub_type', name_type_map['Uint64'], (0, None), (False, None), (None, None)
		yield 'mat_data', name_type_map['ArrayPointer'], (None, name_type_map['PathMaterialData']), (False, None), (None, None)
		yield 'num_data', name_type_map['Uint64'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'elevated_mat', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'elevated_mat_valid', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'elevated_mat_invalid', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'terrain_mat', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'terrain_mat_valid', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'terrain_mat_invalid', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'underside_mat_1', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'underside_mat_2', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'stairs_mat_1', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'stairs_mat_2', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'path_sub_type', name_type_map['Uint64'], (0, None), (False, None)
		yield 'mat_data', name_type_map['ArrayPointer'], (instance.num_data, name_type_map['PathMaterialData']), (False, None)
		yield 'num_data', name_type_map['Uint64'], (0, None), (False, None)

from nifgen.formats.frenderlodspec.imports import name_type_map
from nifgen.formats.ovl_base.compounds.MemStruct import MemStruct


class LodSpecItem(MemStruct):

	__name__ = 'LodSpecItem'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.unknown_1 = name_type_map['Uint'](self.context, 0, None)
		self.max_model_bounding_sphere_radius = name_type_map['Float'](self.context, 0, None)
		self.flags_1 = name_type_map['Ushort'](self.context, 0, None)
		self.flags_2 = name_type_map['Ushort'](self.context, 0, None)
		self.lod_point_0 = name_type_map['Float'](self.context, 0, None)
		self.lod_point_1 = name_type_map['Float'](self.context, 0, None)
		self.lod_point_2 = name_type_map['Float'](self.context, 0, None)
		self.lod_point_3 = name_type_map['Float'](self.context, 0, None)
		self.lod_point_4 = name_type_map['Float'](self.context, 0, None)
		self.pixel_size_off = name_type_map['Float'](self.context, 0, None)
		self.unknown_2 = name_type_map['Uint'](self.context, 0, None)
		self.unknown_3 = name_type_map['Uint'](self.context, 0, None)
		self.unknown_4 = name_type_map['Uint'](self.context, 0, None)
		self.group_name = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'group_name', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'unknown_1', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'max_model_bounding_sphere_radius', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'flags_1', name_type_map['Ushort'], (0, None), (False, None), (None, None)
		yield 'flags_2', name_type_map['Ushort'], (0, None), (False, None), (None, None)
		yield 'lod_point_0', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'lod_point_1', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'lod_point_2', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'lod_point_3', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'lod_point_4', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'pixel_size_off', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'unknown_2', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'unknown_3', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'unknown_4', name_type_map['Uint'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'group_name', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'unknown_1', name_type_map['Uint'], (0, None), (False, None)
		yield 'max_model_bounding_sphere_radius', name_type_map['Float'], (0, None), (False, None)
		yield 'flags_1', name_type_map['Ushort'], (0, None), (False, None)
		yield 'flags_2', name_type_map['Ushort'], (0, None), (False, None)
		yield 'lod_point_0', name_type_map['Float'], (0, None), (False, None)
		yield 'lod_point_1', name_type_map['Float'], (0, None), (False, None)
		yield 'lod_point_2', name_type_map['Float'], (0, None), (False, None)
		yield 'lod_point_3', name_type_map['Float'], (0, None), (False, None)
		yield 'lod_point_4', name_type_map['Float'], (0, None), (False, None)
		yield 'pixel_size_off', name_type_map['Float'], (0, None), (False, None)
		yield 'unknown_2', name_type_map['Uint'], (0, None), (False, None)
		yield 'unknown_3', name_type_map['Uint'], (0, None), (False, None)
		yield 'unknown_4', name_type_map['Uint'], (0, None), (False, None)

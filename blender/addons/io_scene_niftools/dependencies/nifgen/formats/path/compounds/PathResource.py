from nifgen.formats.ovl_base.compounds.MemStruct import MemStruct
from nifgen.formats.path.imports import name_type_map


class PathResource(MemStruct):

	__name__ = 'PathResource'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.path_type = name_type_map['Byte'](self.context, 0, None)
		self.path_sub_type = name_type_map['Byte'](self.context, 0, None)
		self.unk_byte_1 = name_type_map['Byte'].from_value(1)
		self.unk_byte_2 = name_type_map['Byte'](self.context, 0, None)
		self.pathmaterial = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		self.pathextrusion_kerb = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		self.pathextrusion_railing = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		self.pathextrusion_ground = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		self.pathsupport = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'pathmaterial', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'pathextrusion_kerb', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'pathextrusion_railing', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'pathextrusion_ground', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'pathsupport', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'path_type', name_type_map['Byte'], (0, None), (False, None), (None, None)
		yield 'path_sub_type', name_type_map['Byte'], (0, None), (False, None), (None, None)
		yield 'unk_byte_1', name_type_map['Byte'], (0, None), (False, 1), (None, None)
		yield 'unk_byte_2', name_type_map['Byte'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'pathmaterial', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'pathextrusion_kerb', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'pathextrusion_railing', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'pathextrusion_ground', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'pathsupport', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'path_type', name_type_map['Byte'], (0, None), (False, None)
		yield 'path_sub_type', name_type_map['Byte'], (0, None), (False, None)
		yield 'unk_byte_1', name_type_map['Byte'], (0, None), (False, 1)
		yield 'unk_byte_2', name_type_map['Byte'], (0, None), (False, None)

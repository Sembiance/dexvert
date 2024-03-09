from nifgen.formats.matcol.imports import name_type_map
from nifgen.formats.ovl_base.compounds.MemStruct import MemStruct


class LayerFrag(MemStruct):

	__name__ = 'LayerFrag'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.u_0 = name_type_map['Uint64'](self.context, 0, None)
		self.u_1 = name_type_map['Uint64'](self.context, 0, None)
		self.info_count = name_type_map['Uint64'](self.context, 0, None)
		self.u_2 = name_type_map['Uint64'](self.context, 0, None)
		self.u_3 = name_type_map['Uint64'](self.context, 0, None)
		self.attrib_count = name_type_map['Uint64'](self.context, 0, None)
		self.layer_name = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		self.infos = name_type_map['ArrayPointer'](self.context, self.info_count, name_type_map['Info'])
		self.attribs = name_type_map['ArrayPointer'](self.context, self.attrib_count, name_type_map['Attrib'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'layer_name', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'u_0', name_type_map['Uint64'], (0, None), (False, None), (None, None)
		yield 'u_1', name_type_map['Uint64'], (0, None), (False, None), (None, None)
		yield 'infos', name_type_map['ArrayPointer'], (None, name_type_map['Info']), (False, None), (None, None)
		yield 'info_count', name_type_map['Uint64'], (0, None), (False, None), (None, None)
		yield 'u_2', name_type_map['Uint64'], (0, None), (False, None), (None, None)
		yield 'u_3', name_type_map['Uint64'], (0, None), (False, None), (None, None)
		yield 'attribs', name_type_map['ArrayPointer'], (None, name_type_map['Attrib']), (False, None), (None, None)
		yield 'attrib_count', name_type_map['Uint64'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'layer_name', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'u_0', name_type_map['Uint64'], (0, None), (False, None)
		yield 'u_1', name_type_map['Uint64'], (0, None), (False, None)
		yield 'infos', name_type_map['ArrayPointer'], (instance.info_count, name_type_map['Info']), (False, None)
		yield 'info_count', name_type_map['Uint64'], (0, None), (False, None)
		yield 'u_2', name_type_map['Uint64'], (0, None), (False, None)
		yield 'u_3', name_type_map['Uint64'], (0, None), (False, None)
		yield 'attribs', name_type_map['ArrayPointer'], (instance.attrib_count, name_type_map['Attrib']), (False, None)
		yield 'attrib_count', name_type_map['Uint64'], (0, None), (False, None)

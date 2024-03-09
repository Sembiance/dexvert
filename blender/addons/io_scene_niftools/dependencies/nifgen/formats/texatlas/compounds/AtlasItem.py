from nifgen.formats.ovl_base.compounds.MemStruct import MemStruct
from nifgen.formats.texatlas.imports import name_type_map


class AtlasItem(MemStruct):

	__name__ = 'AtlasItem'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.startx = name_type_map['Float'](self.context, 0, None)
		self.starty = name_type_map['Float'](self.context, 0, None)
		self.endx = name_type_map['Float'](self.context, 0, None)
		self.endy = name_type_map['Float'](self.context, 0, None)
		self.layer = name_type_map['Uint'](self.context, 0, None)
		self.flags_1 = name_type_map['Ushort'](self.context, 0, None)
		self.flags_2 = name_type_map['Ushort'](self.context, 0, None)
		self.atlas_name = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'atlas_name', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'startx', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'starty', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'endx', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'endy', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'layer', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'flags_1', name_type_map['Ushort'], (0, None), (False, None), (None, None)
		yield 'flags_2', name_type_map['Ushort'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'atlas_name', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'startx', name_type_map['Float'], (0, None), (False, None)
		yield 'starty', name_type_map['Float'], (0, None), (False, None)
		yield 'endx', name_type_map['Float'], (0, None), (False, None)
		yield 'endy', name_type_map['Float'], (0, None), (False, None)
		yield 'layer', name_type_map['Uint'], (0, None), (False, None)
		yield 'flags_1', name_type_map['Ushort'], (0, None), (False, None)
		yield 'flags_2', name_type_map['Ushort'], (0, None), (False, None)

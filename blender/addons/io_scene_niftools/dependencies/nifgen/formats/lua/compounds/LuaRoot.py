from nifgen.formats.lua.imports import name_type_map
from nifgen.formats.ovl_base.compounds.MemStruct import MemStruct


class LuaRoot(MemStruct):

	"""
	ZTUAC: 32 bytes
	newer: 48 bytes
	all meta data except lua size seems to just be meta data, can be zeroed
	"""

	__name__ = 'LuaRoot'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.lua_size = name_type_map['Uint'](self.context, 0, None)
		self.sixteenk = name_type_map['Uint'](self.context, 0, None)
		self.hash = name_type_map['Uint'](self.context, 0, None)
		self.zero_0 = name_type_map['Uint'](self.context, 0, None)
		self.zero_1 = name_type_map['Uint64'](self.context, 0, None)
		self.zero_2 = name_type_map['Uint64'](self.context, 0, None)
		self.source_path = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		self.likely_alignment = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'lua_size', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'sixteenk', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'hash', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'zero_0', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'source_path', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (lambda context: context.version >= 18, None)
		yield 'likely_alignment', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (lambda context: context.version >= 18, None)
		yield 'zero_1', name_type_map['Uint64'], (0, None), (False, None), (None, None)
		yield 'zero_2', name_type_map['Uint64'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'lua_size', name_type_map['Uint'], (0, None), (False, None)
		yield 'sixteenk', name_type_map['Uint'], (0, None), (False, None)
		yield 'hash', name_type_map['Uint'], (0, None), (False, None)
		yield 'zero_0', name_type_map['Uint'], (0, None), (False, None)
		if instance.context.version >= 18:
			yield 'source_path', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
			yield 'likely_alignment', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'zero_1', name_type_map['Uint64'], (0, None), (False, None)
		yield 'zero_2', name_type_map['Uint64'], (0, None), (False, None)

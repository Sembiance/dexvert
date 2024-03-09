from nifgen.formats.island.imports import name_type_map
from nifgen.formats.ovl_base.compounds.MemStruct import MemStruct


class IslandRoot(MemStruct):

	"""
	JWE2: 32 bytes
	"""

	__name__ = 'IslandRoot'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.a = name_type_map['Float'](self.context, 0, None)
		self.b = name_type_map['Float'](self.context, 0, None)
		self.count = name_type_map['Uint64'](self.context, 0, None)
		self.zero = name_type_map['Uint64'](self.context, 0, None)
		self.path_name = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'path_name', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'a', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'b', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'count', name_type_map['Uint64'], (0, None), (False, None), (None, None)
		yield 'zero', name_type_map['Uint64'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'path_name', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'a', name_type_map['Float'], (0, None), (False, None)
		yield 'b', name_type_map['Float'], (0, None), (False, None)
		yield 'count', name_type_map['Uint64'], (0, None), (False, None)
		yield 'zero', name_type_map['Uint64'], (0, None), (False, None)

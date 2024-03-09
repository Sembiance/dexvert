from nifgen.array import Array
from nifgen.formats.ovl_base.compounds.MemStruct import MemStruct
from nifgen.formats.path.imports import name_type_map


class PathType(MemStruct):

	__name__ = 'PathType'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.enum_value = name_type_map['PathTypes'](self.context, 0, None)
		self._align = Array(self.context, 0, None, (0,), name_type_map['Ubyte'])
		self.min_width = name_type_map['Float'].from_value(4.0)
		self.max_width = name_type_map['Float'].from_value(10.0)
		self._unk_int_2 = name_type_map['Uint'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'enum_value', name_type_map['PathTypes'], (0, None), (False, None), (None, None)
		yield '_align', Array, (0, None, (3,), name_type_map['Ubyte']), (False, None), (None, None)
		yield 'min_width', name_type_map['Float'], (0, None), (False, 4.0), (None, None)
		yield 'max_width', name_type_map['Float'], (0, None), (False, 10.0), (None, None)
		yield '_unk_int_2', name_type_map['Uint'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'enum_value', name_type_map['PathTypes'], (0, None), (False, None)
		yield '_align', Array, (0, None, (3,), name_type_map['Ubyte']), (False, None)
		yield 'min_width', name_type_map['Float'], (0, None), (False, 4.0)
		yield 'max_width', name_type_map['Float'], (0, None), (False, 10.0)
		yield '_unk_int_2', name_type_map['Uint'], (0, None), (False, None)

from nifgen.formats.motiongraph.imports import name_type_map
from nifgen.formats.ovl_base.compounds.MemStruct import MemStruct


class MRFMember1(MemStruct):

	"""
	72 bytes / 144 bytes ?
	"""

	__name__ = 'MRFMember1'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.count_0 = name_type_map['Uint64'](self.context, 0, None)
		self.dtype = name_type_map['Uint64'](self.context, 0, None)
		self.num_children = name_type_map['Uint64'](self.context, 0, None)
		self.count_4 = name_type_map['Uint64'](self.context, 0, None)
		self.lua_method = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		self.ptr_0 = name_type_map['Pointer'](self.context, 0, None)
		self.motiongraph_vars = name_type_map['Pointer'](self.context, self.dtype, name_type_map['MotiongraphVars'])
		self.children = name_type_map['ArrayPointer'](self.context, self.num_children, name_type_map['MRFChild'])
		self.id = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'lua_method', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'count_0', name_type_map['Uint64'], (0, None), (False, None), (None, None)
		yield 'ptr_0', name_type_map['Pointer'], (0, None), (False, None), (None, None)
		yield 'motiongraph_vars', name_type_map['Pointer'], (None, name_type_map['MotiongraphVars']), (False, None), (None, None)
		yield 'dtype', name_type_map['Uint64'], (0, None), (False, None), (None, None)
		yield 'num_children', name_type_map['Uint64'], (0, None), (False, None), (None, None)
		yield 'children', name_type_map['ArrayPointer'], (None, name_type_map['MRFChild']), (False, None), (None, None)
		yield 'count_4', name_type_map['Uint64'], (0, None), (False, None), (None, None)
		yield 'id', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'lua_method', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'count_0', name_type_map['Uint64'], (0, None), (False, None)
		yield 'ptr_0', name_type_map['Pointer'], (0, None), (False, None)
		yield 'motiongraph_vars', name_type_map['Pointer'], (instance.dtype, name_type_map['MotiongraphVars']), (False, None)
		yield 'dtype', name_type_map['Uint64'], (0, None), (False, None)
		yield 'num_children', name_type_map['Uint64'], (0, None), (False, None)
		yield 'children', name_type_map['ArrayPointer'], (instance.num_children, name_type_map['MRFChild']), (False, None)
		yield 'count_4', name_type_map['Uint64'], (0, None), (False, None)
		yield 'id', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)

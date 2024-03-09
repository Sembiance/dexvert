from nifgen.formats.motiongraph.imports import name_type_map
from nifgen.formats.ovl_base.compounds.MemStruct import MemStruct


class MotiongraphHeader(MemStruct):

	"""
	# if self.ovl.context.version > 47:
	"""

	__name__ = 'MotiongraphHeader'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.count_0 = name_type_map['Uint'](self.context, 0, None)
		self.count_1 = name_type_map['Uint'](self.context, 0, None)
		self.root_frag = name_type_map['Pointer'](self.context, 0, name_type_map['MotiongraphRootFrag'])
		self.state_output_entries = name_type_map['Pointer'](self.context, 0, name_type_map['StateArray'])
		self.m_g_two = name_type_map['Pointer'](self.context, 0, name_type_map['MGTwo'])
		self.m_r_f_member_1 = name_type_map['Pointer'](self.context, 0, name_type_map['MRFMember1'])
		self.lua_modules = name_type_map['Pointer'](self.context, 0, name_type_map['LuaModules'])
		self.lua_results = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		self.first_non_transition_state = name_type_map['Pointer'](self.context, 0, name_type_map['MRFMember2'])
		self.empty_str = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'root_frag', name_type_map['Pointer'], (0, name_type_map['MotiongraphRootFrag']), (False, None), (None, None)
		yield 'state_output_entries', name_type_map['Pointer'], (0, name_type_map['StateArray']), (False, None), (None, None)
		yield 'm_g_two', name_type_map['Pointer'], (0, name_type_map['MGTwo']), (False, None), (None, None)
		yield 'm_r_f_member_1', name_type_map['Pointer'], (0, name_type_map['MRFMember1']), (False, None), (None, None)
		yield 'count_0', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'count_1', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'lua_modules', name_type_map['Pointer'], (0, name_type_map['LuaModules']), (False, None), (None, None)
		yield 'lua_results', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'first_non_transition_state', name_type_map['Pointer'], (0, name_type_map['MRFMember2']), (False, None), (None, None)
		yield 'empty_str', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'root_frag', name_type_map['Pointer'], (0, name_type_map['MotiongraphRootFrag']), (False, None)
		yield 'state_output_entries', name_type_map['Pointer'], (0, name_type_map['StateArray']), (False, None)
		yield 'm_g_two', name_type_map['Pointer'], (0, name_type_map['MGTwo']), (False, None)
		yield 'm_r_f_member_1', name_type_map['Pointer'], (0, name_type_map['MRFMember1']), (False, None)
		yield 'count_0', name_type_map['Uint'], (0, None), (False, None)
		yield 'count_1', name_type_map['Uint'], (0, None), (False, None)
		yield 'lua_modules', name_type_map['Pointer'], (0, name_type_map['LuaModules']), (False, None)
		yield 'lua_results', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'first_non_transition_state', name_type_map['Pointer'], (0, name_type_map['MRFMember2']), (False, None)
		yield 'empty_str', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)

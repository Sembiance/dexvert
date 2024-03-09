from nifgen.formats.motiongraph.imports import name_type_map
from nifgen.formats.ovl_base.compounds.MemStruct import MemStruct


class MRFChild(MemStruct):

	"""
	32 bytes
	"""

	__name__ = 'MRFChild'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.count_0 = name_type_map['Uint64'](self.context, 0, None)
		self.count_1 = name_type_map['Uint64'](self.context, 0, None)
		self.m_r_f_member = name_type_map['Pointer'](self.context, 0, name_type_map['MRFMember1'])
		self.ptr_1 = name_type_map['Pointer'](self.context, 0, name_type_map['Something'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'count_0', name_type_map['Uint64'], (0, None), (False, None), (None, None)
		yield 'm_r_f_member', name_type_map['Pointer'], (0, name_type_map['MRFMember1']), (False, None), (None, None)
		yield 'ptr_1', name_type_map['Pointer'], (0, name_type_map['Something']), (False, None), (None, None)
		yield 'count_1', name_type_map['Uint64'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'count_0', name_type_map['Uint64'], (0, None), (False, None)
		yield 'm_r_f_member', name_type_map['Pointer'], (0, name_type_map['MRFMember1']), (False, None)
		yield 'ptr_1', name_type_map['Pointer'], (0, name_type_map['Something']), (False, None)
		yield 'count_1', name_type_map['Uint64'], (0, None), (False, None)

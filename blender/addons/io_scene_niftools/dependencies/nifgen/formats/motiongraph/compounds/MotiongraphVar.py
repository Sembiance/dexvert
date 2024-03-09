from nifgen.formats.motiongraph.imports import name_type_map
from nifgen.formats.ovl_base.compounds.MemStruct import MemStruct


class MotiongraphVar(MemStruct):

	"""
	24 bytes (?)
	"""

	__name__ = 'MotiongraphVar'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.unk = name_type_map['Uint64'](self.context, 0, None)
		self.var_name = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		self.target_name = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'var_name', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'target_name', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'unk', name_type_map['Uint64'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'var_name', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'target_name', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'unk', name_type_map['Uint64'], (0, None), (False, None)

from nifgen.formats.motiongraph.imports import name_type_map
from nifgen.formats.ovl_base.compounds.MemStruct import MemStruct


class Transition(MemStruct):

	"""
	40 bytes
	only used if transition is in 'id'
	"""

	__name__ = 'Transition'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.count_0 = name_type_map['Uint'](self.context, 0, None)
		self.count_1 = name_type_map['Uint'](self.context, 0, None)
		self.count_2 = name_type_map['Uint64'](self.context, 0, None)
		self.ptr_0 = name_type_map['Pointer'](self.context, self.count_1, name_type_map['PtrList'])
		self.ptr_1 = name_type_map['Pointer'](self.context, self.count_2, name_type_map['TransStructArray'])
		self.id = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'count_0', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'count_1', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'ptr_0', name_type_map['Pointer'], (None, name_type_map['PtrList']), (False, None), (None, None)
		yield 'count_2', name_type_map['Uint64'], (0, None), (False, None), (None, None)
		yield 'ptr_1', name_type_map['Pointer'], (None, name_type_map['TransStructArray']), (False, None), (None, None)
		yield 'id', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'count_0', name_type_map['Uint'], (0, None), (False, None)
		yield 'count_1', name_type_map['Uint'], (0, None), (False, None)
		yield 'ptr_0', name_type_map['Pointer'], (instance.count_1, name_type_map['PtrList']), (False, None)
		yield 'count_2', name_type_map['Uint64'], (0, None), (False, None)
		yield 'ptr_1', name_type_map['Pointer'], (instance.count_2, name_type_map['TransStructArray']), (False, None)
		yield 'id', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)

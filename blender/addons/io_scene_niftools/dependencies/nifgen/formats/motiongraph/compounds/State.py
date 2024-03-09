from nifgen.formats.motiongraph.imports import name_type_map
from nifgen.formats.ovl_base.compounds.MemStruct import MemStruct


class State(MemStruct):

	"""
	name uncertain
	40 bytes
	"""

	__name__ = 'State'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.unk = name_type_map['Uint'](self.context, 0, None)
		self.activities_count = name_type_map['Uint'](self.context, 0, None)
		self.count_2 = name_type_map['Uint64'](self.context, 0, None)
		self.activities = name_type_map['Pointer'](self.context, self.activities_count, name_type_map['RefList'])
		self.array_2 = name_type_map['Pointer'](self.context, self.count_2, name_type_map['TransStructStopList'])
		self.id = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'unk', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'activities_count', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'activities', name_type_map['Pointer'], (None, name_type_map['RefList']), (False, None), (None, None)
		yield 'count_2', name_type_map['Uint64'], (0, None), (False, None), (None, None)
		yield 'array_2', name_type_map['Pointer'], (None, name_type_map['TransStructStopList']), (False, None), (None, None)
		yield 'id', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'unk', name_type_map['Uint'], (0, None), (False, None)
		yield 'activities_count', name_type_map['Uint'], (0, None), (False, None)
		yield 'activities', name_type_map['Pointer'], (instance.activities_count, name_type_map['RefList']), (False, None)
		yield 'count_2', name_type_map['Uint64'], (0, None), (False, None)
		yield 'array_2', name_type_map['Pointer'], (instance.count_2, name_type_map['TransStructStopList']), (False, None)
		yield 'id', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)

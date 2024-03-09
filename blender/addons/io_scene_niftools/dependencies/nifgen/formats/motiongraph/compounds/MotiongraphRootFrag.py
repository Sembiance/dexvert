from nifgen.formats.motiongraph.imports import name_type_map
from nifgen.formats.ovl_base.compounds.MemStruct import MemStruct


class MotiongraphRootFrag(MemStruct):

	"""
	64 bytes
	"""

	__name__ = 'MotiongraphRootFrag'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.num_activities = name_type_map['Uint64'](self.context, 0, None)
		self.count_1 = name_type_map['Uint64'](self.context, 0, None)
		self.count_2 = name_type_map['Uint64'](self.context, 0, None)
		self.num_xmls = name_type_map['Uint64'](self.context, 0, None)
		self.activities = name_type_map['Pointer'](self.context, self.num_activities, name_type_map['Activities'])
		self.ptr_1 = name_type_map['Pointer'](self.context, self.count_1, name_type_map['MRFArray1'])
		self.ptr_2 = name_type_map['Pointer'](self.context, self.count_2, name_type_map['MRFArray2'])
		self.ptr_xmls = name_type_map['Pointer'](self.context, self.num_xmls, name_type_map['XMLArray'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'num_activities', name_type_map['Uint64'], (0, None), (False, None), (None, None)
		yield 'activities', name_type_map['Pointer'], (None, name_type_map['Activities']), (False, None), (None, None)
		yield 'count_1', name_type_map['Uint64'], (0, None), (False, None), (None, None)
		yield 'ptr_1', name_type_map['Pointer'], (None, name_type_map['MRFArray1']), (False, None), (None, None)
		yield 'count_2', name_type_map['Uint64'], (0, None), (False, None), (None, None)
		yield 'ptr_2', name_type_map['Pointer'], (None, name_type_map['MRFArray2']), (False, None), (None, None)
		yield 'num_xmls', name_type_map['Uint64'], (0, None), (False, None), (None, None)
		yield 'ptr_xmls', name_type_map['Pointer'], (None, name_type_map['XMLArray']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'num_activities', name_type_map['Uint64'], (0, None), (False, None)
		yield 'activities', name_type_map['Pointer'], (instance.num_activities, name_type_map['Activities']), (False, None)
		yield 'count_1', name_type_map['Uint64'], (0, None), (False, None)
		yield 'ptr_1', name_type_map['Pointer'], (instance.count_1, name_type_map['MRFArray1']), (False, None)
		yield 'count_2', name_type_map['Uint64'], (0, None), (False, None)
		yield 'ptr_2', name_type_map['Pointer'], (instance.count_2, name_type_map['MRFArray2']), (False, None)
		yield 'num_xmls', name_type_map['Uint64'], (0, None), (False, None)
		yield 'ptr_xmls', name_type_map['Pointer'], (instance.num_xmls, name_type_map['XMLArray']), (False, None)

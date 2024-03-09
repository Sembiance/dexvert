from nifgen.formats.ovl_base.compounds.MemStruct import MemStruct
from nifgen.formats.path.imports import name_type_map


class PathJoinPartResourceRoot(MemStruct):

	__name__ = 'PathJoinPartResourceRoot'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.num_res = name_type_map['Uint64'](self.context, 0, None)
		self.resources_list = name_type_map['ArrayPointer'](self.context, self.num_res, name_type_map['PathJoinPartResource'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'resources_list', name_type_map['ArrayPointer'], (None, name_type_map['PathJoinPartResource']), (False, None), (None, None)
		yield 'num_res', name_type_map['Uint64'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'resources_list', name_type_map['ArrayPointer'], (instance.num_res, name_type_map['PathJoinPartResource']), (False, None)
		yield 'num_res', name_type_map['Uint64'], (0, None), (False, None)

from nifgen.formats.motiongraph.imports import name_type_map
from nifgen.formats.ovl_base.compounds.MemStruct import MemStruct


class ActivityAnimationInfo(MemStruct):

	"""
	?
	"""

	__name__ = 'ActivityAnimationInfo'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.offset = name_type_map['Float'](self.context, 0, None)
		self.weight = name_type_map['Uint'](self.context, 0, None)
		self.activity_name = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'activity_name', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'offset', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'weight', name_type_map['Uint'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'activity_name', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'offset', name_type_map['Float'], (0, None), (False, None)
		yield 'weight', name_type_map['Uint'], (0, None), (False, None)

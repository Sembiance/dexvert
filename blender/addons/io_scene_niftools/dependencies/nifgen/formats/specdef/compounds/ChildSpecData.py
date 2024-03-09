from nifgen.formats.ovl_base.compounds.MemStruct import MemStruct
from nifgen.formats.specdef.imports import name_type_map


class ChildSpecData(MemStruct):

	"""
	8 bytes
	eg. spineflex.specdef points to dependency for another specdef
	eg. flatridecontroller.specdef points to SpecdefRoot
	"""

	__name__ = 'ChildSpecData'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.specdef = name_type_map['Pointer'](self.context, 0, name_type_map['SpecdefRoot'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'specdef', name_type_map['Pointer'], (0, name_type_map['SpecdefRoot']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'specdef', name_type_map['Pointer'], (0, name_type_map['SpecdefRoot']), (False, None)

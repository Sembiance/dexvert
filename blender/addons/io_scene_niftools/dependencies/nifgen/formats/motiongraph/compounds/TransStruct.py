from nifgen.formats.motiongraph.imports import name_type_map
from nifgen.formats.ovl_base.compounds.MemStruct import MemStruct


class TransStruct(MemStruct):

	"""
	24 bytes
	"""

	__name__ = 'TransStruct'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.states = name_type_map['StateArray'](self.context, 0, None)
		self.another_mrfentry_2 = name_type_map['Pointer'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'another_mrfentry_2', name_type_map['Pointer'], (0, None), (False, None), (None, None)
		yield 'states', name_type_map['StateArray'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'another_mrfentry_2', name_type_map['Pointer'], (0, None), (False, None)
		yield 'states', name_type_map['StateArray'], (0, None), (False, None)

from nifgen.formats.motiongraph.imports import name_type_map
from nifgen.formats.ovl_base.compounds.MemStruct import MemStruct


class TransStructStop(MemStruct):

	"""
	24 bytes
	actually same as above, just don't keep reading here
	"""

	__name__ = 'TransStructStop'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.another_mrfentry_2 = name_type_map['Reference'](self.context, 0, None)
		self.other_states = name_type_map['MGTwo'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'another_mrfentry_2', name_type_map['Reference'], (0, None), (False, None), (None, None)
		yield 'other_states', name_type_map['MGTwo'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'another_mrfentry_2', name_type_map['Reference'], (0, None), (False, None)
		yield 'other_states', name_type_map['MGTwo'], (0, None), (False, None)

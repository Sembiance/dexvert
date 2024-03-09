from nifgen.array import Array
from nifgen.formats.dinosaurmaterialvariants.imports import name_type_map
from nifgen.formats.ovl_base.compounds.MemStruct import MemStruct


class PatternArray(MemStruct):

	__name__ = 'PatternArray'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.patterns = Array(self.context, 0, None, (0,), name_type_map['Pattern'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'patterns', Array, (0, None, (None,), name_type_map['Pattern']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'patterns', Array, (0, None, (instance.arg,), name_type_map['Pattern']), (False, None)

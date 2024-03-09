from nifgen.array import Array
from nifgen.formats.ovl_base.compounds.MemStruct import MemStruct
from nifgen.formats.renderparameters.imports import name_type_map


class CurveList(MemStruct):

	"""
	this is not null ptr terminated, but padded to 16 bytes at the end
	"""

	__name__ = 'CurveList'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.ptrs = Array(self.context, 0, name_type_map['KeyPoint'], (0,), name_type_map['Pointer'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'ptrs', Array, (0, name_type_map['KeyPoint'], (None,), name_type_map['Pointer']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'ptrs', Array, (0, name_type_map['KeyPoint'], (instance.arg,), name_type_map['Pointer']), (False, None)

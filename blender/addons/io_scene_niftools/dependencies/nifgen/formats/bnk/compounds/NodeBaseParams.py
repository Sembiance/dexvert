from nifgen.array import Array
from nifgen.base_struct import BaseStruct
from nifgen.formats.bnk.imports import name_type_map


class NodeBaseParams(BaseStruct):

	__name__ = 'NodeBaseParams'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.raw = Array(self.context, 0, None, (0,), name_type_map['Byte'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'raw', Array, (0, None, (30,), name_type_map['Byte']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'raw', Array, (0, None, (30,), name_type_map['Byte']), (False, None)

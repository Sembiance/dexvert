from nifgen.array import Array
from nifgen.base_struct import BaseStruct
from nifgen.formats.ms2.imports import name_type_map


class MinusPadding(BaseStruct):

	"""
	Used in PC
	"""

	__name__ = 'MinusPadding'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# -1
		self.indices = Array(self.context, 0, None, (0,), name_type_map['Short'])

		# 0
		self.padding = Array(self.context, 0, None, (0,), name_type_map['Byte'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'indices', Array, (0, None, (None,), name_type_map['Short']), (False, None), (None, None)
		yield 'padding', Array, (0, None, (None,), name_type_map['Byte']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'indices', Array, (0, None, (instance.arg,), name_type_map['Short']), (False, None)
		yield 'padding', Array, (0, None, ((16 - ((instance.arg * 2) % 16)) % 16,), name_type_map['Byte']), (False, None)

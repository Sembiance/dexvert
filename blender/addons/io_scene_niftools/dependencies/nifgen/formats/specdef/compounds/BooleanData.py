from nifgen.array import Array
from nifgen.formats.ovl_base.compounds.MemStruct import MemStruct
from nifgen.formats.specdef.imports import name_type_map


class BooleanData(MemStruct):

	"""
	8 bytes in log
	"""

	__name__ = 'BooleanData'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.ivalue = name_type_map['Ubyte'](self.context, 0, None)
		self.ioptional = name_type_map['Ubyte'](self.context, 0, None)
		self.unused = Array(self.context, 0, None, (0,), name_type_map['Ubyte'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'ivalue', name_type_map['Ubyte'], (0, None), (False, None), (None, None)
		yield 'ioptional', name_type_map['Ubyte'], (0, None), (False, None), (None, None)
		yield 'unused', Array, (0, None, (6,), name_type_map['Ubyte']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'ivalue', name_type_map['Ubyte'], (0, None), (False, None)
		yield 'ioptional', name_type_map['Ubyte'], (0, None), (False, None)
		yield 'unused', Array, (0, None, (6,), name_type_map['Ubyte']), (False, None)

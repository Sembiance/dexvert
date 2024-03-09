from nifgen.array import Array
from nifgen.base_struct import BaseStruct
from nifgen.formats.ms2.imports import name_type_map


class FloatsY(BaseStruct):

	__name__ = 'FloatsY'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.floats = Array(self.context, 0, None, (0,), name_type_map['Float'])
		self.index = name_type_map['Uint'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'floats', Array, (0, None, (8,), name_type_map['Float']), (False, None), (None, None)
		yield 'index', name_type_map['Uint'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'floats', Array, (0, None, (8,), name_type_map['Float']), (False, None)
		yield 'index', name_type_map['Uint'], (0, None), (False, None)
